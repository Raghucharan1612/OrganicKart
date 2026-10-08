import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useAuth } from "@/hooks/useAuth";
import { useLanguage } from "@/i18n/LanguageContext";
import { logout, updateProfile } from "@/store/slices/authSlice";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { validatePhone, validateRequired } from "@/utils/validators";
import userService from "@/services/userService";
import { getApiErrorMessage } from "@/utils/errorUtils";

export default function ProfilePage() {
  const { user } = useAuth();
  const { t } = useLanguage();
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const [form, setForm] = useState({ full_name: "", phone: "" });
  const [fieldErrors, setFieldErrors] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ current_password: "", new_password: "", confirm_password: "" });
  const [showPasswords, setShowPasswords] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({ full_name: user.full_name || "", phone: user.phone || "" });
    }
  }, [user]);

  if (!user) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (fieldErrors[name]) setFieldErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const errors = {
      full_name: validateRequired(form.full_name, "Full name"),
      phone: validatePhone(form.phone),
    };
    setFieldErrors(errors);
    return Object.values(errors).every((msg) => !msg);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setIsSaving(true);
    const result = await dispatch(updateProfile({ ...form, phone: form.phone || null }));
    setIsSaving(false);

    if (updateProfile.fulfilled.match(result)) {
      toast.success("Profile updated.");
    } else {
      toast.error(result.payload || "Could not update profile.");
    }
  };

  const handleLogout = () => {
    dispatch(logout());
    toast.success("Logged out successfully.");
    navigate("/login");
  };

  const handlePasswordChange = async (event) => {
    event.preventDefault();
    if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
      setPasswordError("Complete all password fields.");
      return;
    }
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError("New password and confirmation do not match.");
      return;
    }

    setIsChangingPassword(true);
    setPasswordError("");
    try {
      await userService.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
      });
      setPasswordForm({ current_password: "", new_password: "", confirm_password: "" });
      toast.success("Password changed successfully.");
    } catch (error) {
      setPasswordError(getApiErrorMessage(error, "Could not change password."));
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-primary-900">My Profile</h1>
        <p className="mt-1 text-sm text-gray-500">Manage your account details.</p>
      </div>

      <div className="card grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Email</p>
          <p className="mt-1 text-sm text-gray-800">{user.email}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Role</p>
          <p className="mt-1">
            <span className="rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-700">
              {user.role}
            </span>
          </p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Account status</p>
          <p className="mt-1 text-sm text-gray-800">{user.is_active ? "Active" : "Deactivated"}</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-400">Verified</p>
          <p className="mt-1 text-sm text-gray-800">{user.is_verified ? "Yes" : "Not yet verified"}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="card space-y-4" noValidate>
        <h2 className="font-display text-lg font-semibold text-primary-900">Edit details</h2>

        <Input
          id="full_name"
          name="full_name"
          label="Full name"
          value={form.full_name}
          onChange={handleChange}
          error={fieldErrors.full_name}
        />

        <Input
          id="phone"
          name="phone"
          label="Phone"
          placeholder="+91 98765 43210"
          value={form.phone}
          onChange={handleChange}
          error={fieldErrors.phone}
        />

        <Button type="submit" isLoading={isSaving}>
          Save changes
        </Button>
      </form>

      <form onSubmit={handlePasswordChange} className="card space-y-4" noValidate>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="font-display text-lg font-semibold text-primary-900">{t("security")}</h2>
            <p className="mt-1 text-sm text-gray-500">{t("securityDescription")}</p>
          </div>
          <button
            type="button"
            onClick={() => setShowPasswords((visible) => !visible)}
            aria-pressed={showPasswords}
            className="shrink-0 text-sm font-semibold text-primary-700 hover:underline"
          >
            {showPasswords ? t("hidePasswords") : t("showPasswords")}
          </button>
        </div>

        {passwordError && <p className="rounded-xl border border-red-100 bg-red-50 p-3 text-sm text-red-700">{passwordError}</p>}

        <Input id="current_password" name="current_password" type={showPasswords ? "text" : "password"} autoComplete="current-password" label={t("currentPassword")} value={passwordForm.current_password} onChange={(event) => setPasswordForm((current) => ({ ...current, current_password: event.target.value }))} />
        <Input id="new_password" name="new_password" type={showPasswords ? "text" : "password"} autoComplete="new-password" label={t("newPassword")} value={passwordForm.new_password} onChange={(event) => setPasswordForm((current) => ({ ...current, new_password: event.target.value }))} />
        <Input id="confirm_password" name="confirm_password" type={showPasswords ? "text" : "password"} autoComplete="new-password" label={t("confirmNewPassword")} value={passwordForm.confirm_password} onChange={(event) => setPasswordForm((current) => ({ ...current, confirm_password: event.target.value }))} />

        <div className="flex flex-wrap items-center justify-between gap-3">
          <Link to={`/forgot-password?email=${encodeURIComponent(user.email)}`} className="text-sm font-semibold text-primary-700 hover:underline">
            {t("forgotPassword")}
          </Link>
          <Button type="submit" isLoading={isChangingPassword}>{t("changePassword")}</Button>
        </div>
      </form>

      <div className="card flex items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-lg font-semibold text-primary-900">Sign out</h2>
          <p className="mt-1 text-sm text-gray-500">Sign out securely on this device.</p>
        </div>
        <Button type="button" variant="secondary" onClick={handleLogout}>Logout</Button>
      </div>
    </div>
  );
}
