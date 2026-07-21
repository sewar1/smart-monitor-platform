import type { TranslationSet, LanguageCode } from '../types/login.types';

// =========================================================================
// LOCALIZATION TRANSLATION MATRIX (EN & DE)
// =========================================================================
export const translations: Record<LanguageCode, TranslationSet> = {
  en: {
    titleMain: "Infrastructure Monitor",
    titleSub: "Administrative Access Portal",
    lblUsername: "Username or Corporate Email",
    lblPassword: "Password",
    lnkForgot: "Forgot Password?",
    btnSubmit: "Secure Login",
    modalTitle: "Password Recovery Matrix",
    modalDesc: "Please contact your system DevSecOps cluster administrator to manually verify identity and trigger a credential reset token vector.",
    modalClose: "Close",
    langBtn: "DE",
    userShort: "Identity parameter requires minimum 5 characters.",
    userSuccess: "Authorized identity string structure mapped successfully.",
    passShort: "Minimum 4 characters required.",
    passWeak: "Password needs uppercase, lowercase, number, and a symbol.",
    passSuccess: "Cryptographic entropy guidelines fulfilled successfully."
  },
  de: {
    titleMain: "Infrastruktur-Monitor",
    titleSub: "Administratives Zugangsportal",
    lblUsername: "Benutzername oder Firmen-E-Mail",
    lblPassword: "Passwort",
    lnkForgot: "Passwort vergessen?",
    btnSubmit: "Sicherer Login",
    modalTitle: "Passwort-Wiederherstellung",
    modalDesc: "Bitte kontaktieren Sie Ihren DevSecOps Cluster Administrator, um Ihre Identität zu verifizieren.",
    modalClose: "Schließen",
    langBtn: "EN",
    userShort: "Identitätsparameter erfordert mindestens 5 Zeichen.",
    userSuccess: "Autorisierte Identitätsstruktur erfolgreich zugeordnet.",
    passShort: "Mindestens 4 Zeichen erforderlich.",
    passWeak: "Passwort erfordert Groß-, Kleinbuchstaben, Zahl und Symbol.",
    passSuccess: "Kryptografische Entropie-Richtlinien erfolgreich erfüllt."
  }
};