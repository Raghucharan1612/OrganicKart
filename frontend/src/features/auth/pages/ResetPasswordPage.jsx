import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import toast from "react-hot-toast";
import authService from "@/services/authService";
import Input from "@/components/Input";
import Button from "@/components/Button";
import { useLanguage } from "@/i18n/LanguageContext";
import { getApiErrorMessage } from "@/utils/errorUtils";
import { validatePassword } from "@/utils/validators";

export default function ResetPasswordPage() {
  const { t } = useLanguage();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [showPasswords, setShowPasswords] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const passwordError = validatePassword(password);
    if (passwordError) {
      setError(passwordError);
      return;
    }
    if (password !== confirmation) {
      setError("Passwords do not match.");
      return;
    }
    if (!token) {
      setError("This password reset link is invalid or expired. Request a new link.");
      return;
    }

    setIsSubmitting(true);
    setError("");
    try {
      await authService.resetPassword({ token, new_password: password });
      toast.success("Password reset. You can now sign in.");
      navigate("/login", { replace: true });
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, "Could not reset your password."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-md">
      <div className="card">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h1 className="font-display text-2xl font-bold text-primary-900">{t("resetTitle")}</h1>
            <p className="mt-1 text-sm text-gray-500">{t("resetDescription")}</p>
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

        <form onSubmit={handleSubmit} className="mt-6 space-y-4" noValidate>
          <Input
            id="new-password"
            name="new-password"
            type={showPasswords ? "text" : "password"}
            label={t("newPassword")}
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <Input
            id="confirm-password"
            name="confirm-password"
            type={showPasswords ? "text" : "password"}
            label={t("confirmNewPassword")}
            autoComplete="new-password"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
          />
          {error && <p role="alert" className="rounded-lg border border-red-100 bg-red-50 p-3 text-sm text-red-700">{error}</p>}
          <Button type="submit" isLoading={isSubmitting} className="w-full">{t("resetPassword")}</Button>
        </form>

        <p className="mt-5 text-center text-sm text-gray-500">
          <Link to="/forgot-password" className="font-medium text-primary-700 hover:underline">{t("requestAnotherLink")}</Link>
        </p>
      </div>
    </div>
  );
}