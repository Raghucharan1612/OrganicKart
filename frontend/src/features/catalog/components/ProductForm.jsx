import { useEffect, useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";
import ImageUploadManager from "@/components/vendor/ImageUploadManager";
import { validateRequired } from "@/utils/validators";

const EMPTY_FORM = {
  name: "",
  description: "",
  category_id: "",
  price: "",
  stock_quantity: "0",
  unit: "kg",
  image_url: "",
  is_organic_certified: false,
  certification_number: "",
  farm_name: "",
};

const UNIT_OPTIONS = [
  "100g",
  "200g",
  "250g",
  "500g",
  "1kg",
  "kg",
  "g",
  "500ml",
  "1 litre",
  "litre",
  "ml",
  "piece",
  "pack",
  "dozen",
  "bunch",
];

export default function ProductForm({
  categories = [],
  initialValues = null,
  onSubmit,
  onCancel = null,
  isSaving = false,
  onImagesUpdated = null,
}) {
  const [form, setForm] = useState({ ...EMPTY_FORM, ...initialValues });
  const [fieldErrors, setFieldErrors] = useState({});
  const [pendingFiles, setPendingFiles] = useState([]);
  const [pendingPrimaryIndex, setPendingPrimaryIndex] = useState(0);
  const [pendingUrls, setPendingUrls] = useState([]);

  const isEditing = Boolean(initialValues?.id);

  useEffect(() => {
    if (initialValues) {
      setForm({
        ...EMPTY_FORM,
        ...initialValues,
        category_id: initialValues.category?.id ?? initialValues.category_id ?? "",
      });
    }
  }, [initialValues]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({ ...prev, [name]: type === "checkbox" ? checked : value }));
    if (fieldErrors[name]) setFieldErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const errors = {
      name: validateRequired(form.name, "Product name"),
      category_id: validateRequired(form.category_id, "Category"),
      price: !form.price || Number(form.price) <= 0 ? "Enter a valid positive price." : "",
      stock_quantity:
        form.stock_quantity === "" || Number(form.stock_quantity) < 0
          ? "Stock quantity cannot be negative."
          : "",
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    const payload = {
      ...form,
      category_id: Number(form.category_id),
      price: Number(form.price),
      stock_quantity: Number(form.stock_quantity) || 0,
      certification_number: form.certification_number || null,
      farm_name: form.farm_name || null,
      image_url: form.image_url || null,
      description: form.description || null,
    };

    onSubmit(payload, pendingFiles, pendingPrimaryIndex, pendingUrls);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6" noValidate>
      {/* Product Basic Info Card */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 space-y-4 shadow-2xs">
        <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2.5">
          General Information
        </h3>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <Input
              id="name"
              name="name"
              label="Product Name *"
              placeholder="e.g. Fresh Organic Kashmiri Apples"
              value={form.name}
              onChange={handleChange}
              error={fieldErrors.name}
            />
          </div>

          <div className="sm:col-span-2">
            <label htmlFor="description" className="mb-1.5 block text-xs font-semibold text-slate-700">
              Description
            </label>
            <textarea
              id="description"
              name="description"
              rows={3}
              value={form.description || ""}
              onChange={handleChange}
              placeholder="Describe farming practices, taste profile, origin, and organic quality..."
              className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-800 placeholder-slate-400 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition"
            />
          </div>

          <div>
            <label htmlFor="category_id" className="mb-1.5 block text-xs font-semibold text-slate-700">
              Category *
            </label>
            <select
              id="category_id"
              name="category_id"
              value={form.category_id}
              onChange={handleChange}
              className={`w-full rounded-xl border bg-white px-3.5 py-2 text-xs text-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition ${
                fieldErrors.category_id ? "border-rose-400" : "border-slate-200"
              }`}
            >
              <option value="">Select an organic category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
            {fieldErrors.category_id && (
              <p className="mt-1 text-xs text-rose-600">{fieldErrors.category_id}</p>
            )}
          </div>

          <div>
            <label htmlFor="unit" className="mb-1.5 block text-xs font-semibold text-slate-700">
              Selling Unit *
            </label>
            <select
              id="unit"
              name="unit"
              value={form.unit}
              onChange={handleChange}
              className="w-full rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs text-slate-800 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-hidden transition"
            >
              {UNIT_OPTIONS.map((u) => (
                <option key={u} value={u}>
                  {u}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Input
              id="price"
              name="price"
              type="number"
              step="0.01"
              min="0"
              label="Price (₹) *"
              placeholder="0.00"
              value={form.price}
              onChange={handleChange}
              error={fieldErrors.price}
            />
          </div>

          <div>
            <Input
              id="stock_quantity"
              name="stock_quantity"
              type="number"
              min="0"
              label="Stock Available (units) *"
              placeholder="0"
              value={form.stock_quantity}
              onChange={handleChange}
              error={fieldErrors.stock_quantity}
            />
          </div>
        </div>
      </div>

      {/* Integrated Image Upload Manager Section */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 shadow-2xs">
        <ImageUploadManager
          productId={isEditing ? initialValues.id : null}
          pendingFiles={pendingFiles}
          onPendingFilesChange={(files, primaryIdx) => {
            setPendingFiles(files);
            setPendingPrimaryIndex(primaryIdx);
          }}
          pendingUrls={pendingUrls}
          onPendingUrlsChange={setPendingUrls}
          onImagesUpdated={onImagesUpdated}
        />
      </div>

      {/* Organic Certification Details Section */}
      <div className="bg-white border border-slate-200/80 rounded-2xl p-5 sm:p-6 space-y-4 shadow-2xs">
        <h3 className="text-sm font-bold text-slate-900 border-b border-slate-100 pb-2.5">
          Organic Trust &amp; Certification
        </h3>

        <label className="flex items-center gap-2.5 text-xs font-medium text-slate-700 cursor-pointer">
          <input
            type="checkbox"
            name="is_organic_certified"
            checked={form.is_organic_certified}
            onChange={handleChange}
            className="h-4 w-4 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500"
          />
          <span>This product is certified organic by an authorized agency (e.g. NPOP, Jaivik Bharat, USDA)</span>
        </label>

        {form.is_organic_certified && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 pt-2">
            <Input
              id="certification_number"
              name="certification_number"
              label="Certification / License Number"
              placeholder="e.g. ORG-2024-8841"
              value={form.certification_number || ""}
              onChange={handleChange}
            />
            <Input
              id="farm_name"
              name="farm_name"
              label="Farm / Producer Brand Name"
              placeholder="e.g. Green Valley Agro"
              value={form.farm_name || ""}
              onChange={handleChange}
            />
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 pt-2">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={isSaving}
            className="px-4 py-2 rounded-xl border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold transition"
          >
            Cancel
          </button>
        )}
        <Button type="submit" isLoading={isSaving} className="!bg-emerald-600 hover:!bg-emerald-700 !text-white !text-xs !font-semibold !px-5 !py-2.5 !rounded-xl shadow-2xs">
          {isEditing ? "Save & Submit Changes" : "Create Product & Submit"}
        </Button>
      </div>
    </form>
  );
}
