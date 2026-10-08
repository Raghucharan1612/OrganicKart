import { createContext, useContext, useEffect, useState } from "react";

const translations = {
  en: {
    language: "Language",
    deliveryTime: "10-Min Delivery",
    promotion: "Fresh & 100% Organic • Best Prices Guaranteed",
    support: "Support: 1800-ORGANIC",
    deliverTo: "Deliver to",
    chooseLocation: "Choose location",
    catalog: "Catalog",
    orders: "Orders",
    login: "Login",
    signUp: "Sign Up",
    security: "Security",
    securityDescription: "Change your password using your current password for verification.",
    currentPassword: "Current Password",
    newPassword: "New Password",
    confirmNewPassword: "Confirm New Password",
    showPasswords: "Show passwords",
    hidePasswords: "Hide passwords",
    forgotPassword: "Forgot password?",
    changePassword: "Change Password",
    fullName: "Full name",
    email: "Email address",
    phone: "Phone number",
    phonePlaceholder: "+91 98765 43210",
    phoneRequired: "Phone number is required.",
    welcomeBack: "Welcome back",
    loginDescription: "Log in to your OrganicKart account.",
    newToOrganicKart: "New to OrganicKart?",
    yourPassword: "Your password",
    createAccount: "Create your account",
    joinMarketplace: "Join OrganicKart's organic marketplace.",
    passwordHint: "At least 8 characters",
    signupRole: "I am signing up as",
    customerRole: "Customer — shop for organic produce",
    farmerRole: "Farmer — sell what you grow",
    vendorRole: "Vendor — run an organic store",
    deliveryRole: "Delivery Partner — fulfil deliveries",
    createAccountButton: "Create account",
    existingAccount: "Already have an account?",
    rememberPassword: "Remember your password?",
    resetRequestSubmitted: "If an account exists for that email, password reset instructions have been sent.",
    logIn: "Log in",
    forgotTitle: "Reset your password",
    forgotDescription: "Enter your account email and we’ll send a password reset link.",
    sendResetLink: "Send reset link",
    resetTitle: "Choose a new password",
    resetDescription: "Use at least 8 characters with a letter and a number.",
    resetPassword: "Reset password",
    requestAnotherLink: "Request another reset link",
  },
  kn: {
    language: "ಭಾಷೆ",
    deliveryTime: "10 ನಿಮಿಷಗಳಲ್ಲಿ ವಿತರಣೆ",
    promotion: "ತಾಜಾ ಮತ್ತು 100% ಸಾವಯವ • ಉತ್ತಮ ಬೆಲೆಗಳ ಭರವಸೆ",
    support: "ಸಹಾಯ: 1800-ORGANIC",
    deliverTo: "ವಿತರಣೆ ವಿಳಾಸ",
    chooseLocation: "ಸ್ಥಳ ಆಯ್ಕೆಮಾಡಿ",
    catalog: "ಉತ್ಪನ್ನಗಳು",
    orders: "ಆರ್ಡರ್‌ಗಳು",
    login: "ಲಾಗಿನ್",
    signUp: "ನೋಂದಣಿ",
    security: "ಭದ್ರತೆ",
    securityDescription: "ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಲು ಪ್ರಸ್ತುತ ಪಾಸ್‌ವರ್ಡ್ ನಮೂದಿಸಿ.",
    currentPassword: "ಪ್ರಸ್ತುತ ಪಾಸ್‌ವರ್ಡ್",
    newPassword: "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್",
    confirmNewPassword: "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
    showPasswords: "ಪಾಸ್‌ವರ್ಡ್ ತೋರಿಸಿ",
    hidePasswords: "ಪಾಸ್‌ವರ್ಡ್ ಮರೆಮಾಡಿ",
    forgotPassword: "ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?",
    changePassword: "ಪಾಸ್‌ವರ್ಡ್ ಬದಲಾಯಿಸಿ",
    fullName: "ಪೂರ್ಣ ಹೆಸರು",
    email: "ಇಮೇಲ್ ವಿಳಾಸ",
    phone: "ದೂರವಾಣಿ ಸಂಖ್ಯೆ",
    phonePlaceholder: "+91 98765 43210",
    phoneRequired: "ದೂರವಾಣಿ ಸಂಖ್ಯೆ ಅಗತ್ಯವಿದೆ.",
    welcomeBack: "ಮರಳಿ ಸ್ವಾಗತ",
    loginDescription: "ನಿಮ್ಮ OrganicKart ಖಾತೆಗೆ ಲಾಗಿನ್ ಮಾಡಿ.",
    newToOrganicKart: "OrganicKart ಗೆ ಹೊಸಬರೇ?",
    yourPassword: "ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್",
    createAccount: "ಖಾತೆ ತೆರೆಯಿರಿ",
    joinMarketplace: "OrganicKart ಸಾವಯವ ಮಾರುಕಟ್ಟೆಗೆ ಸೇರಿ.",
    passwordHint: "ಕನಿಷ್ಠ 8 ಅಕ್ಷರಗಳು",
    signupRole: "ನಾನು ಈ ಪಾತ್ರದಲ್ಲಿ ನೋಂದಾಯಿಸುತ್ತಿದ್ದೇನೆ",
    customerRole: "ಗ್ರಾಹಕ — ಸಾವಯವ ಉತ್ಪನ್ನಗಳನ್ನು ಖರೀದಿಸಿ",
    farmerRole: "ರೈತ — ಬೆಳೆದ ಉತ್ಪನ್ನಗಳನ್ನು ಮಾರಾಟ ಮಾಡಿ",
    vendorRole: "ವ್ಯಾಪಾರಿ — ಸಾವಯವ ಅಂಗಡಿ ನಿರ್ವಹಿಸಿ",
    deliveryRole: "ವಿತರಣಾ ಪಾಲುದಾರ — ಆರ್ಡರ್‌ಗಳನ್ನು ತಲುಪಿಸಿ",
    createAccountButton: "ಖಾತೆ ರಚಿಸಿ",
    existingAccount: "ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?",
    rememberPassword: "ನಿಮ್ಮ ಪಾಸ್‌ವರ್ಡ್ ನೆನಪಿದೆಯೇ?",
    resetRequestSubmitted: "ಈ ಇಮೇಲ್‌ಗೆ ಖಾತೆ ಇದ್ದರೆ, ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸುವ ಸೂಚನೆಗಳನ್ನು ಕಳುಹಿಸಲಾಗಿದೆ.",
    logIn: "ಲಾಗಿನ್ ಮಾಡಿ",
    forgotTitle: "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ",
    forgotDescription: "ನಿಮ್ಮ ಖಾತೆಯ ಇಮೇಲ್ ನಮೂದಿಸಿ; ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕಳುಹಿಸುತ್ತೇವೆ.",
    sendResetLink: "ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕಳುಹಿಸಿ",
    resetTitle: "ಹೊಸ ಪಾಸ್‌ವರ್ಡ್ ಆಯ್ಕೆಮಾಡಿ",
    resetDescription: "ಕನಿಷ್ಠ 8 ಅಕ್ಷರಗಳು, ಒಂದು ಅಕ್ಷರ ಮತ್ತು ಒಂದು ಸಂಖ್ಯೆ ಬಳಸಿ.",
    resetPassword: "ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ",
    requestAnotherLink: "ಮತ್ತೊಂದು ಮರುಹೊಂದಿಸುವ ಲಿಂಕ್ ಕೇಳಿ",
  },
};

const LanguageContext = createContext({ language: "en", setLanguage: () => {}, t: (key) => key });

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => localStorage.getItem("organickart_language") === "kn" ? "kn" : "en");

  useEffect(() => {
    localStorage.setItem("organickart_language", language);
    document.documentElement.lang = language;
  }, [language]);

  const t = (key) => translations[language][key] || translations.en[key] || key;

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
