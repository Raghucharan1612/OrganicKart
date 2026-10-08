import { useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";
import geocodingService from "@/services/geocodingService";
import { validateRequired } from "@/utils/validators";

const EMPTY_FORM = {
  label: "Home",
  recipient_name: "",
  phone: "",
  address_line1: "",
  address_line2: "",
  city: "",
  state: "",
  postal_code: "",
  country: "India",
  is_default: false,
  latitude: null,
  longitude: null,
};

export default function AddressForm({ initialValues, onSubmit, onCancel, isSaving }) {
  const [form, setForm] = useState({ ...EMPTY_FORM, ...initialValues });
  const [fieldErrors, setFieldErrors] = useState({});
  const [locationError, setLocationError] = useState("");
  const [isLocating, setIsLocating] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    if (fieldErrors[name]) setFieldErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const errors = {
      recipient_name: validateRequired(form.recipient_name, "Recipient name"),
      phone: validateRequired(form.phone, "Phone"),
      address_line1: validateRequired(form.address_line1, "Address line 1"),
      city: validateRequired(form.city, "City"),
      state: validateRequired(form.state, "State"),
      postal_code: validateRequired(form.postal_code, "Postal code"),
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const useCurrentLocation = () => {
    setLocationError("");
    if (!navigator.geolocation) {
      setLocationError("Geolocation is unavailable in this browser. Please enter your address manually.");
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        const coordinates = { latitude: coords.latitude, longitude: coords.longitude };
        try {
          const address = await geocodingService.reverse(coords.latitude, coords.longitude);
          setForm((current) => ({ ...current, ...address, ...coordinates }));
        } catch {
          setForm((current) => ({ ...current, ...coordinates }));
          setLocationError("Location found, but its address could not be filled automatically. Please complete the address fields.");
        } finally {
          setIsLocating(false);
        }
      },
      (error) => {
        const messages = {
          [error.PERMISSION_DENIED]: "Location access was denied. Please enter your address manually.",
          [error.POSITION_UNAVAILABLE]: "Your location is unavailable. Please enter your address manually.",
          [error.TIMEOUT]: "Location request timed out. Please try again or enter your address manually.",
        };
        setLocationError(messages[error.code] || "Could not retrieve your location. Please enter your address manually.");
        setIsLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input id="label" name="label" label="Label" value={form.label} onChange={handleChange} />
        <Input
          id="recipient_name"
          name="recipient_name"
          label="Recipient name"
          value={form.recipient_name}
          onChange={handleChange}
          error={fieldErrors.recipient_name}
        />
      </div>

      <Input
        id="phone"
        name="phone"
        label="Phone"
        value={form.phone}
        onChange={handleChange}
        error={fieldErrors.phone}
      />

      <Input
        id="address_line1"
        name="address_line1"
        label="Address line 1"
        value={form.address_line1}
        onChange={handleChange}
        error={fieldErrors.address_line1}
      />
      <Input id="address_line2" name="address_line2" label="Address line 2 (optional)" value={form.address_line2} onChange={handleChange} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Input id="city" name="city" label="City" value={form.city} onChange={handleChange} error={fieldErrors.city} />
        <Input id="state" name="state" label="State" value={form.state} onChange={handleChange} error={fieldErrors.state} />
        <Input
          id="postal_code"
          name="postal_code"
          label="Postal code"
          value={form.postal_code}
          onChange={handleChange}
          error={fieldErrors.postal_code}
        />
      </div>

      <Input id="country" name="country" label="Country" value={form.country} onChange={handleChange} />

      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          name="is_default"
          checked={form.is_default}
          onChange={handleChange}
          className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        Set as default address
      </label>

      <div className="rounded-xl border border-primary-100 bg-primary-50/50 p-3 text-sm">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-primary-900">Use your live location, then confirm the editable address fields above.</p>
          <Button type="button" variant="secondary" onClick={useCurrentLocation} isLoading={isLocating}>
            {isLocating ? "Finding address…" : "Use my current location"}
          </Button>
        </div>
        {form.latitude != null && form.longitude != null && (
          <>
            <p className="mt-2 text-xs text-primary-700">
              Location found: {Number(form.latitude).toFixed(5)}, {Number(form.longitude).toFixed(5)}. Please confirm the postal address before saving.
            </p>
            <p className="mt-1 text-xs text-primary-700">
              Address details by <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer" className="underline">OpenStreetMap contributors</a>.
            </p>
          </>
        )}
        {locationError && <p className="mt-2 text-xs text-red-600">{locationError}</p>}
      </div>

      <div className="flex gap-3">
        <Button type="submit" isLoading={isSaving}>
          Save address
        </Button>
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  );
}
