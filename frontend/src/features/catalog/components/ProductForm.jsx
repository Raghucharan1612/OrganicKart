import { useEffect, useState } from "react";
import Input from "@/components/Input";
import Button from "@/components/Button";
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

const UNIT_OPTIONS = ["100g", "200g", "250g", "500g", "1kg", "kg", "g", "500ml", "1 litre", "litre", "ml", "piece", "pack", "dozen", "bunch"];

export default function ProductForm({ categories, initialValues, onSubmit, onCancel, isSaving }) {
  const [form, setForm] = useState({ ...EMPTY_FORM, ...initialValues });
  const [fieldErrors, setFieldErrors] = useState({});

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
      price: !form.price || Number(form.price) <= 0 ? "Enter a valid price." : "",
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    onSubmit({
      ...form,
      category_id: Number(form.category_id),
      price: Number(form.price),
      stock_quantity: Number(form.stock_quantity) || 0,
      certification_number: form.certification_number || null,
      farm_name: form.farm_name || null,
      image_url: form.image_url || null,
      description: form.description || null,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4" noValidate>
      <Input
        id="name"
        name="name"
        label="Product name"
        value={form.name}
        onChange={handleChange}
        error={fieldErrors.name}
      />

      <div>
        <label htmlFor="description" className="mb-1.5 block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          id="description"
          name="description"
          rows={3}
          value={form.description}
          onChange={handleChange}
          className="input-field"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label htmlFor="category_id" className="mb-1.5 block text-sm font-medium text-gray-700">
            Category
          </label>
          <select
            id="category_id"
            name="category_id"
            value={form.category_id}
            onChange={handleChange}
            className={`input-field ${fieldErrors.category_id ? "border-red-400" : ""}`}
          >
            <option value="">Select a category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
          {fieldErrors.category_id && (
            <p className="mt-1 text-xs text-red-600">{fieldErrors.category_id}</p>
          )}
        </div>

        <div>
          <label htmlFor="unit" className="mb-1.5 block text-sm font-medium text-gray-700">
            Unit
          </label>
          <select id="unit" name="unit" value={form.unit} onChange={handleChange} className="input-field">
            {UNIT_OPTIONS.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Input
          id="price"
          name="price"
          type="number"
          step="0.01"
          min="0"
          label="Price (₹)"
          value={form.price}
          onChange={handleChange}
          error={fieldErrors.price}
        />
        <Input
          id="stock_quantity"
          name="stock_quantity"
          type="number"
          min="0"
          label="Stock quantity"
          value={form.stock_quantity}
          onChange={handleChange}
        />
      </div>

      <Input id="image_url" name="image_url" label="Image URL (optional)" value={form.image_url} onChange={handleChange} />

      <label className="flex items-center gap-2 text-sm text-gray-700">
        <input
          type="checkbox"
          name="is_organic_certified"
          checked={form.is_organic_certified}
          onChange={handleChange}
          className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
        />
        This product is organic certified
      </label>

      {form.is_organic_certified && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input
            id="certification_number"
            name="certification_number"
            label="Certification number"
            value={form.certification_number}
            onChange={handleChange}
          />
          <Input id="farm_name" name="farm_name" label="Farm / brand name" value={form.farm_name} onChange={handleChange} />
        </div>
      )}

      <div className="flex gap-3 pt-2">
        <Button type="submit" isLoading={isSaving}>
          Save product
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
