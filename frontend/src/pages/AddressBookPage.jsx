import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import addressService from "@/services/addressService";
import AddressForm from "@/features/auth/components/AddressForm";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import EmptyState from "@/components/EmptyState";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function AddressBookPage() {
  const [addresses, setAddresses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formMode, setFormMode] = useState(null); // null | "create" | address.id being edited
  const [loadError, setLoadError] = useState("");

  const loadAddresses = async () => {
    setIsLoading(true);
    setLoadError("");
    try {
      const data = await addressService.list();
      setAddresses(data);
    } catch (err) {
      setLoadError("Could not load your addresses. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAddresses();
  }, []);

  const handleCreate = async (payload) => {
    setIsSaving(true);
    try {
      await addressService.create(payload);
      toast.success("Address added.");
      setFormMode(null);
      await loadAddresses();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not add address."));
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdate = async (addressId, payload) => {
    setIsSaving(true);
    try {
      await addressService.update(addressId, payload);
      toast.success("Address updated.");
      setFormMode(null);
      await loadAddresses();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not update address."));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (addressId) => {
    if (!window.confirm("Delete this address?")) return;
    try {
      await addressService.remove(addressId);
      toast.success("Address removed.");
      await loadAddresses();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not delete address."));
    }
  };

  const editingAddress =
    typeof formMode === "number" ? addresses.find((a) => a.id === formMode) : null;

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary-900">My Addresses</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your saved delivery addresses.</p>
        </div>
        {formMode === null && (
          <Button onClick={() => setFormMode("create")}>+ Add address</Button>
        )}
      </div>

      {formMode === "create" && (
        <div className="card">
          <h2 className="mb-4 font-display text-lg font-semibold text-primary-900">New address</h2>
          <AddressForm onSubmit={handleCreate} onCancel={() => setFormMode(null)} isSaving={isSaving} />
        </div>
      )}

      {editingAddress && (
        <div className="card">
          <h2 className="mb-4 font-display text-lg font-semibold text-primary-900">Edit address</h2>
          <AddressForm
            initialValues={editingAddress}
            onSubmit={(payload) => handleUpdate(editingAddress.id, payload)}
            onCancel={() => setFormMode(null)}
            isSaving={isSaving}
          />
        </div>
      )}

      {isLoading ? (
        <Spinner label="Loading your addresses…" />
      ) : loadError ? (
        <div className="card text-center text-sm text-red-600">{loadError}</div>
      ) : addresses.length === 0 && formMode === null ? (
        <EmptyState
          title="No addresses yet"
          description="Add your first delivery address to speed up checkout later."
          action={<Button onClick={() => setFormMode("create")}>+ Add address</Button>}
        />
      ) : (
        <div className="space-y-3">
          {addresses.map((addr) => (
            <div key={addr.id} className="card flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-primary-900">{addr.label}</span>
                  {addr.is_default && (
                    <span className="rounded-full bg-accent-100 px-2 py-0.5 text-xs font-medium text-accent-700">
                      Default
                    </span>
                  )}
                </div>
                <p className="mt-1 text-sm text-gray-600">
                  {addr.recipient_name} · {addr.phone}
                </p>
                <p className="text-sm text-gray-500">
                  {addr.address_line1}
                  {addr.address_line2 ? `, ${addr.address_line2}` : ""}, {addr.city}, {addr.state} {addr.postal_code},{" "}
                  {addr.country}
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button
                  onClick={() => setFormMode(addr.id)}
                  className="text-sm font-medium text-primary-700 hover:underline"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(addr.id)}
                  className="text-sm font-medium text-red-600 hover:underline"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
