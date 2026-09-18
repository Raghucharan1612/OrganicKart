import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import categoryService from "@/services/categoryService";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import { validateRequired } from "@/utils/validators";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formMode, setFormMode] = useState(null); // null | "create" | category.id
  const [form, setForm] = useState({ name: "", description: "" });
  const [fieldError, setFieldError] = useState("");

  const loadCategories = async () => {
    setIsLoading(true);
    try {
      const data = await categoryService.list(true); // include inactive for admin view
      setCategories(data);
    } catch (err) {
      toast.error("Could not load categories.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  const startCreate = () => {
    setForm({ name: "", description: "" });
    setFieldError("");
    setFormMode("create");
  };

  const startEdit = (category) => {
    setForm({ name: category.name, description: category.description || "" });
    setFieldError("");
    setFormMode(category.id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const error = validateRequired(form.name, "Category name");
    setFieldError(error);
    if (error) return;

    setIsSaving(true);
    try {
      if (formMode === "create") {
        await categoryService.create(form);
        toast.success("Category created.");
      } else {
        await categoryService.update(formMode, form);
        toast.success("Category updated.");
      }
      setFormMode(null);
      await loadCategories();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not save category."));
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeactivate = async (id) => {
    if (!window.confirm("Deactivate this category? Existing products keep their reference.")) return;
    try {
      await categoryService.deactivate(id);
      toast.success("Category deactivated.");
      await loadCategories();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not deactivate category."));
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary-900">Manage Categories</h1>
          <p className="mt-1 text-sm text-gray-500">Admin-only: the taxonomy every seller lists products under.</p>
        </div>
        {formMode === null && <Button onClick={startCreate}>+ Add category</Button>}
      </div>

      {formMode !== null && (
        <form onSubmit={handleSubmit} className="card space-y-4">
          <h2 className="font-display text-lg font-semibold text-primary-900">
            {formMode === "create" ? "New category" : "Edit category"}
          </h2>
          <Input
            id="cat-name"
            label="Name"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            error={fieldError}
          />
          <div>
            <label htmlFor="cat-desc" className="mb-1.5 block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              id="cat-desc"
              rows={2}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              className="input-field"
            />
          </div>
          <div className="flex gap-3">
            <Button type="submit" isLoading={isSaving}>
              Save
            </Button>
            <Button type="button" variant="secondary" onClick={() => setFormMode(null)}>
              Cancel
            </Button>
          </div>
        </form>
      )}

      {isLoading ? (
        <Spinner label="Loading categories…" />
      ) : (
        <div className="space-y-2">
          {categories.map((c) => (
            <div key={c.id} className="card flex items-center justify-between py-3">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-primary-900">{c.name}</span>
                  {!c.is_active && (
                    <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                      Inactive
                    </span>
                  )}
                </div>
                {c.description && <p className="text-sm text-gray-500">{c.description}</p>}
              </div>
              <div className="flex shrink-0 gap-3">
                <button onClick={() => startEdit(c)} className="text-sm font-medium text-primary-700 hover:underline">
                  Edit
                </button>
                {c.is_active && (
                  <button
                    onClick={() => handleDeactivate(c.id)}
                    className="text-sm font-medium text-red-600 hover:underline"
                  >
                    Deactivate
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
