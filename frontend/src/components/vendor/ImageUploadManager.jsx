import { useState, useRef, useEffect } from "react";
import toast from "react-hot-toast";
import productService from "@/services/productService";
import { getProductImageUrl, validateImageFile, SUPPORTED_IMAGE_TYPES } from "@/utils/imageUtils";
import { getApiErrorMessage } from "@/utils/errorUtils";

/**
 * ImageUploadManager
 *
 * Props:
 * - productId: number | null (if editing an existing product)
 * - pendingFiles: array of local files (for new product creation before ID exists)
 * - onPendingFilesChange: callback(files, primaryIndex)
 * - onImagesUpdated: callback() when server images change
 */
export default function ImageUploadManager({
  productId = null,
  pendingFiles = [],
  onPendingFilesChange = null,
  pendingUrls = [],
  onPendingUrlsChange = null,
  onImagesUpdated = null,
}) {
  const fileInputRef = useRef(null);
  const replaceInputRef = useRef(null);

  // Server-side images state (for existing product)
  const [serverImages, setServerImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);

  // Active operations state
  const [uploadProgress, setUploadProgress] = useState(null); // 0 to 100
  const [isUploading, setIsUploading] = useState(false);
  const [actionImageId, setActionImageId] = useState(null); // image id currently being replaced/deleted
  const [replacingTargetId, setReplacingTargetId] = useState(null);

  // Local pending files state (when creating new product before saving)
  const [localFiles, setLocalFiles] = useState([]);
  const [primaryLocalIndex, setPrimaryLocalIndex] = useState(0);
  const [localUrls, setLocalUrls] = useState([]);
  const [urlInput, setUrlInput] = useState("");

  // Synchronize with parent's pendingFiles
  useEffect(() => {
    if (!productId && pendingFiles) {
      setLocalFiles(pendingFiles);
    }
  }, [productId, pendingFiles]);

  useEffect(() => {
    if (!productId) setLocalUrls(pendingUrls);
  }, [productId, pendingUrls]);

  const handleAddUrl = async () => {
    const url = urlInput.trim();
    if (!/^https?:\/\//i.test(url)) {
      toast.error("Enter a valid HTTP or HTTPS image URL.");
      return;
    }
    if (productId) {
      try {
        await productService.addImageUrl(productId, url);
        setUrlInput("");
        await loadServerImages();
        onImagesUpdated?.();
      } catch (err) {
        toast.error(getApiErrorMessage(err, "Could not add image URL."));
      }
      return;
    }
    if (localFiles.length + localUrls.length >= 10) {
      toast.error("Maximum 10 images allowed per product.");
      return;
    }
    const updated = [...localUrls, url];
    setLocalUrls(updated);
    onPendingUrlsChange?.(updated);
    setUrlInput("");
  };

  const loadServerImages = async () => {
    if (!productId) return;
    setIsLoading(true);
    setLoadError(null);
    try {
      const data = await productService.getImages(productId);
      setServerImages(Array.isArray(data) ? data : []);
    } catch (err) {
      const msg = getApiErrorMessage(err, "Failed to load product images.");
      setLoadError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (productId) {
      loadServerImages();
    }
  }, [productId]);

  // Handle local pending files addition (for new product)
  const handleAddLocalFiles = (selectedFiles) => {
    const valid = [];
    for (const f of selectedFiles) {
      const err = validateImageFile(f);
      if (err) {
        toast.error(`${f.name}: ${err}`);
      } else {
        valid.push(f);
      }
    }

    if (valid.length === 0) return;

    if (localFiles.length + valid.length > 10) {
      toast.error("Maximum 10 images allowed per product.");
      return;
    }

    const updated = [...localFiles, ...valid];
    setLocalFiles(updated);
    if (onPendingFilesChange) {
      onPendingFilesChange(updated, primaryLocalIndex);
    }
  };

  // Upload files to server (for existing product)
  const handleUploadToServer = async (selectedFiles) => {
    if (!productId) return;

    const valid = [];
    for (const f of selectedFiles) {
      const err = validateImageFile(f);
      if (err) {
        toast.error(`${f.name}: ${err}`);
      } else {
        valid.push(f);
      }
    }

    if (valid.length === 0) return;

    if (serverImages.length + valid.length > 10) {
      toast.error(`Maximum 10 images allowed. Product already has ${serverImages.length}.`);
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      await productService.uploadImages(productId, valid, (event) => {
        if (event.total) {
          const percent = Math.round((event.loaded * 100) / event.total);
          setUploadProgress(percent);
        }
      });
      toast.success(`${valid.length} image${valid.length > 1 ? "s" : ""} uploaded successfully!`);
      await loadServerImages();
      if (onImagesUpdated) onImagesUpdated();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Upload failed. Please check file format and size."));
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  const handleFileInputChange = (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;

    if (productId) {
      handleUploadToServer(files);
    } else {
      handleAddLocalFiles(files);
    }
    e.target.value = "";
  };

  // Server actions
  const handleDeleteServerImage = async (imageId) => {
    if (!productId) return;
    setActionImageId(imageId);
    try {
      await productService.deleteImage(productId, imageId);
      toast.success("Image removed.");
      await loadServerImages();
      if (onImagesUpdated) onImagesUpdated();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not delete image."));
    } finally {
      setActionImageId(null);
    }
  };

  const handleSetPrimaryServerImage = async (imageId) => {
    if (!productId) return;
    setActionImageId(imageId);
    try {
      await productService.setPrimaryImage(productId, imageId);
      toast.success("Primary image updated.");
      await loadServerImages();
      if (onImagesUpdated) onImagesUpdated();
    } catch (err) {
      toast.error(getApiErrorMessage(err, "Could not set primary image."));
    } finally {
      setActionImageId(null);
    }
  };

  const handleTriggerReplace = (imageId) => {
    setReplacingTargetId(imageId);
    if (replaceInputRef.current) {
      replaceInputRef.current.click();
    }
  };

  const handleReplaceServerImage = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !replacingTargetId || !productId) return;

    const err = validateImageFile(file);
    if (err) {
      toast.error(err);
      return;
    }

    setActionImageId(replacingTargetId);
    try {
      await productService.replaceImage(productId, replacingTargetId, file);
      toast.success("Image replaced successfully.");
      await loadServerImages();
      if (onImagesUpdated) onImagesUpdated();
    } catch (error) {
      toast.error(getApiErrorMessage(error, "Failed to replace image."));
    } finally {
      setActionImageId(null);
      setReplacingTargetId(null);
    }
  };

  // Local actions (for pending files before product is saved)
  const handleRemoveLocalFile = (index) => {
    const updated = localFiles.filter((_, i) => i !== index);
    let nextPrimary = primaryLocalIndex;
    if (primaryLocalIndex === index) {
      nextPrimary = 0;
    } else if (primaryLocalIndex > index) {
      nextPrimary = primaryLocalIndex - 1;
    }
    setLocalFiles(updated);
    setPrimaryLocalIndex(nextPrimary);
    if (onPendingFilesChange) {
      onPendingFilesChange(updated, nextPrimary);
    }
  };

  const handleSetPrimaryLocal = (index) => {
    setPrimaryLocalIndex(index);
    if (onPendingFilesChange) {
      onPendingFilesChange(localFiles, index);
    }
  };

  return (
    <div className="space-y-4">
      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={SUPPORTED_IMAGE_TYPES.join(",")}
        onChange={handleFileInputChange}
        className="hidden"
      />
      <input
        ref={replaceInputRef}
        type="file"
        accept={SUPPORTED_IMAGE_TYPES.join(",")}
        onChange={handleReplaceServerImage}
        className="hidden"
      />

      {/* Upload Zone / Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
        <div>
          <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
            <span>📷 Product Images</span>
            <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              {productId ? `${serverImages.length}/10 uploaded` : `${localFiles.length}/10 selected`}
            </span>
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            Supported formats: JPEG, PNG, WebP, AVIF &bull; Max 5MB per file &bull; Up to 10 photos
          </p>
        </div>

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || (productId ? serverImages.length >= 10 : localFiles.length >= 10)}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 active:scale-95 text-white text-xs font-semibold shadow-2xs transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>+ Add Images</span>
        </button>
      </div>

      <div className="flex gap-2">
        <input
          type="url"
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
          placeholder="https://example.com/product-image.jpg"
          className="min-w-0 flex-1 rounded-xl border border-slate-200 px-3 py-2 text-xs focus:border-emerald-500 focus:outline-none"
        />
        <button type="button" onClick={handleAddUrl} className="rounded-xl border border-emerald-600 px-3 py-2 text-xs font-semibold text-emerald-700 hover:bg-emerald-50">
          Add URL
        </button>
      </div>

      {/* Progress Bar */}
      {isUploading && uploadProgress !== null && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-3 space-y-1.5">
          <div className="flex justify-between text-xs font-semibold text-emerald-900">
            <span>Uploading product images...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="h-2 w-full rounded-full bg-emerald-100 overflow-hidden">
            <div
              className="h-full bg-emerald-600 rounded-full transition-all duration-200"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Load error banner */}
      {loadError && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800 flex items-center justify-between">
          <span>⚠️ {loadError}</span>
          <button
            type="button"
            onClick={loadServerImages}
            className="font-semibold underline hover:text-rose-900"
          >
            Retry
          </button>
        </div>
      )}

      {/* Case 1: Editing Existing Product (Server Images) */}
      {productId ? (
        isLoading ? (
          <div className="py-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
            <span>Loading gallery...</span>
          </div>
        ) : serverImages.length === 0 ? (
          <div className="rounded-2xl border-2 border-dashed border-emerald-200/80 bg-emerald-50/30 p-8 text-center">
            <div className="text-3xl mb-2">🌿</div>
            <p className="text-xs font-bold text-slate-800">No images uploaded yet</p>
            <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
              Add clear organic product photos to increase customer confidence and trust. The first image will be set as primary.
            </p>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="mt-3.5 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-2xs"
            >
              Choose Photos
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {serverImages.map((img) => {
              const isActioning = actionImageId === img.id;
              return (
                <div
                  key={img.id}
                  className={`group relative flex flex-col rounded-xl border bg-white overflow-hidden shadow-2xs transition-all ${
                    img.is_primary ? "border-emerald-500 ring-2 ring-emerald-500/20" : "border-slate-200 hover:border-slate-300"
                  }`}
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-square w-full bg-slate-50 overflow-hidden">
                    <img
                      src={getProductImageUrl(img.url)}
                      alt={img.original_filename}
                      className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-200"
                      onError={(e) => {
                        e.currentTarget.src = "/images/product-placeholder.svg";
                      }}
                    />

                    {/* Primary Badge */}
                    {img.is_primary ? (
                      <span className="absolute top-2 left-2 inline-flex items-center gap-1 rounded-md bg-emerald-700 text-white text-[10px] font-bold px-2 py-0.5 shadow-sm">
                        ★ Primary
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleSetPrimaryServerImage(img.id)}
                        disabled={isActioning}
                        className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 rounded-md bg-black/60 hover:bg-emerald-700 text-white text-[10px] font-semibold px-2 py-0.5 transition"
                      >
                        Set Primary
                      </button>
                    )}

                    {/* Loading overlay for this image */}
                    {isActioning && (
                      <div className="absolute inset-0 bg-white/70 backdrop-blur-2xs flex items-center justify-center">
                        <span className="h-4 w-4 animate-spin rounded-full border-2 border-emerald-600 border-t-transparent" />
                      </div>
                    )}
                  </div>

                  {/* Info and Actions */}
                  <div className="p-2 bg-white flex flex-col justify-between gap-1.5 border-t border-slate-100">
                    <p className="text-[11px] font-medium text-slate-700 truncate" title={img.original_filename || img.external_url}>
                      {img.original_filename || img.url_label || "External image"}
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span>{img.image_type === "URL" ? "External URL" : `${(img.file_size / 1024).toFixed(0)} KB`}</span>
                      <div className="flex items-center gap-1.5">
                        {img.image_type !== "URL" && <button
                          type="button"
                          onClick={() => handleTriggerReplace(img.id)}
                          disabled={isActioning}
                          className="font-semibold text-emerald-700 hover:text-emerald-900"
                        >
                          Replace
                        </button>}
                        <span>&bull;</span>
                        <button
                          type="button"
                          onClick={() => handleDeleteServerImage(img.id)}
                          disabled={isActioning}
                          className="font-semibold text-rose-600 hover:text-rose-800"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : (
        /* Case 2: New Product Form (Pending Local Previews) */
        localFiles.length === 0 ? (
          <div className="rounded-2xl border-2 border-dashed border-emerald-200/80 bg-emerald-50/30 p-8 text-center">
            <div className="text-3xl mb-2">🌿</div>
            <p className="text-xs font-bold text-slate-800">Add product photos</p>
            <p className="text-[11px] text-slate-500 mt-1 max-w-sm mx-auto">
              Select multiple photos from your device. You can preview, choose the primary image, and remove or replace before submitting.
            </p>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="mt-3.5 inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold transition shadow-2xs"
            >
              Select Photos
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {localFiles.map((file, idx) => {
              const previewUrl = URL.createObjectURL(file);
              const isPrimary = primaryLocalIndex === idx;
              return (
                <div
                  key={`${file.name}-${idx}`}
                  className={`group relative flex flex-col rounded-xl border bg-white overflow-hidden shadow-2xs transition-all ${
                    isPrimary ? "border-emerald-500 ring-2 ring-emerald-500/20" : "border-slate-200"
                  }`}
                >
                  <div className="relative aspect-square w-full bg-slate-50 overflow-hidden">
                    <img src={previewUrl} alt={file.name} className="h-full w-full object-cover" />

                    {isPrimary ? (
                      <span className="absolute top-2 left-2 rounded-md bg-emerald-700 text-white text-[10px] font-bold px-2 py-0.5 shadow-sm">
                        ★ Primary
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleSetPrimaryLocal(idx)}
                        className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 rounded-md bg-black/60 hover:bg-emerald-700 text-white text-[10px] font-semibold px-2 py-0.5 transition"
                      >
                        Set Primary
                      </button>
                    )}
                  </div>

                  <div className="p-2 bg-white flex flex-col justify-between gap-1 border-t border-slate-100">
                    <p className="text-[11px] font-medium text-slate-700 truncate" title={file.name}>
                      {file.name}
                    </p>
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span>{(file.size / 1024).toFixed(0)} KB</span>
                      <button
                        type="button"
                        onClick={() => handleRemoveLocalFile(idx)}
                        className="font-semibold text-rose-600 hover:text-rose-800"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )
      )}

      {!productId && localUrls.length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {localUrls.map((url, index) => (
            <div key={url} className="relative overflow-hidden rounded-xl border border-slate-200 bg-white">
              <img src={url} alt="External product preview" className="aspect-square w-full object-cover" onError={(e) => { e.currentTarget.style.display = "none"; }} />
              <button type="button" className="absolute right-1 top-1 rounded bg-white px-2 py-1 text-[10px] font-semibold text-rose-600" onClick={() => {
                const updated = localUrls.filter((_, itemIndex) => itemIndex !== index);
                setLocalUrls(updated);
                onPendingUrlsChange?.(updated);
              }}>Remove</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
