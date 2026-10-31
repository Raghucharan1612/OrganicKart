import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import categoryService from "@/services/categoryService";
import Input from "@/components/Input";
import Button from "@/components/Button";
import Spinner from "@/components/Spinner";
import { validateRequired } from "@/utils/validators";
import { getApiErrorMessage } from "@/utils/errorUtils";
import { validateImageFile } from "@/utils/imageUtils";

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [formMode, setFormMode] = useState(null); // null | "create" | category.id
  const [form, setForm] = useState({ name: "", description: "", image_url: "" });
  const [imageSource, setImageSource] = useState("url");
  const [imageFile, setImageFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [deactivateCategory, setDeactivateCategory] = useState(null);
  const [isDeactivating, setIsDeactivating] = useState(false);

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
    setForm({ name: "", description: "", image_url: "" });
    setFieldError("");
    setImageSource("url");
    setImageFile(null);
    setPreviewUrl("");
    setFormMode("create");
  };

  const startEdit = (category) => {
    setForm({ name: category.name, description: category.description || "", image_url: category.image_url || "" });
    setFieldError("");
    setImageSource(category.image_source === "UPLOAD" ? "upload" : "url");
    setImageFile(null);
    setPreviewUrl(category.image_url || "");
    setFormMode(category.id);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const error = validateRequired(form.name, "Category name");
    setFieldError(error);
    if (error) return;

    setIsSaving(true);
    try {
      const categoryPayload = { ...form, image_url: imageSource === "url" ? (form.image_url || null) : null };
      let saved;
      if (formMode === "create") {
        saved = await categoryService.create(categoryPayload);
        toast.success("Category created.");
      } else {
        saved = await categoryService.update(formMode, categoryPayload);
        toast.success("Category updated.");
      }
      if (imageSource === "upload" && imageFile) {
        await categoryService.uploadImage(saved.id, imageFile);
      }
      setFormMode(null);
      await loadCategories();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not save category."));
    } finally {
      setIsSaving(false);
    }
  };

  const confirmDeactivate = async () => {
    if (!deactivateCategory) return;
    setIsDeactivating(true);
    try {
      await categoryService.deactivate(deactivateCategory.id);
      toast.success(`Category "${deactivateCategory.name}" deactivated.`);
      setDeactivateCategory(null);
      await loadCategories();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not deactivate category."));
    } finally {
      setIsDeactivating(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-screen-2xl space-y-6 px-4 py-6 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 rounded-2xl border border-primary-100 bg-white p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between sm:p-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-primary-900">Manage Categories</h1>
          <p className="mt-1 text-sm text-gray-500">Admin-only: the taxonomy every seller lists products under.</p>
        </div>
        {formMode === null && <Button onClick={startCreate}>+ Add category</Button>}
      </div>

      {formMode !== null && (
        <form onSubmit={handleSubmit} className="space-y-5 rounded-2xl border border-gray-100 bg-white p-5 shadow-sm sm:p-6">
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
          <div>
            <label className="mb-1.5 block text-sm font-medium text-gray-700">Category image</label>
            <div className="mb-2 flex gap-4 text-sm text-gray-600">
              <label><input type="radio" checked={imageSource === "url"} onChange={() => setImageSource("url")} /> External URL</label>
              <label><input type="radio" checked={imageSource === "upload"} onChange={() => setImageSource("upload")} /> Upload file</label>
            </div>
            {imageSource === "url" ? (
              <input
                id="cat-image-url"
                type="url"
                placeholder="https://images.example.com/category.jpg"
                value={form.image_url}
                onChange={(e) => { setForm((f) => ({ ...f, image_url: e.target.value })); setPreviewUrl(e.target.value); }}
                className="input-field"
              />
            ) : (
              <input
                type="file"
                accept="image/jpeg,image/png,image/webp,image/avif"
                className="input-field"
                onChange={(e) => {
                  const file = e.target.files?.[0] || null;
                  const error = file && validateImageFile(file);
                  if (error) { setFieldError(error); return; }
                  setImageFile(file);
                  setPreviewUrl(file ? URL.createObjectURL(file) : "");
                }}
              />
            )}
            {previewUrl && (
              <img
                src={previewUrl}
                alt="Preview"
                className="mt-2 h-16 w-16 rounded-xl object-cover border border-gray-200"
                onError={(e) => { e.currentTarget.style.display = "none"; }}
              />
            )}
            {formMode !== "create" && previewUrl && (
              <button type="button" className="mt-2 text-xs font-semibold text-red-600 hover:underline" onClick={async () => {
                try { await categoryService.removeImage(formMode); setForm((f) => ({ ...f, image_url: "" })); setImageFile(null); setPreviewUrl(""); toast.success("Category image removed."); } catch (err) { toast.error(getApiErrorMessage(err, "Could not remove image.")); }
              }}>Remove current image</button>
            )}
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
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {categories.map((c) => (
            <div key={c.id} className="flex items-center justify-between rounded-2xl border border-gray-100 bg-white p-4 shadow-sm transition hover:border-primary-200 hover:shadow-md">
              <div className="flex items-center gap-3">
                {c.image_url ? (
                  <img
                    src={c.image_url}
                    alt={c.name}
                    loading="lazy"
                    decoding="async"
                    width="40"
                    height="40"
                    className="h-10 w-10 rounded-lg object-cover border border-gray-200 shrink-0"
                    onError={(event) => {
                      event.currentTarget.style.display = "none";
                      event.currentTarget.nextElementSibling?.classList.remove("hidden");
                    }}
                  />
                ) : null}
                <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-gray-200 bg-primary-50 text-lg ${c.image_url ? "hidden" : ""}`}>🌿</div>
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
              </div>
              <div className="flex shrink-0 gap-3">
                <button onClick={() => startEdit(c)} className="text-sm font-medium text-primary-700 hover:underline">
                  Edit
                </button>
                {c.is_active && (
                  <button
                    onClick={() => setDeactivateCategory(c)}
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

      {/* In-app Deactivation Confirmation Modal */}
      {deactivateCategory && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-xs animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl space-y-4">
            <h3 className="font-display text-lg font-bold text-gray-900">
              Deactivate "{deactivateCategory.name}"?
            </h3>
            <p className="text-sm text-gray-600">
              This category will no longer be available to customers. Existing products will keep their reference.
            </p>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setDeactivateCategory(null)} disabled={isDeactivating}>
                Cancel
              </Button>
              <Button
                className="!bg-red-600 hover:!bg-red-700 !text-white"
                onClick={confirmDeactivate}
                isLoading={isDeactivating}
              >
                Deactivate
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
