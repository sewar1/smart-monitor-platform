import React, { useState, useEffect } from 'react';
import { LangSwitcher } from './components/LangSwitcher';
import { ValidationMessage } from './components/ValidationMessage';
import { RecoveryModal } from './components/RecoveryModal';

// =========================================================================
// TYPES & INTERFACES DEFINITIONS
// =========================================================================
interface TranslationSet {
  titleMain: string;
  titleSub: string;
  lblUsername: string;
  lblPassword: string;
  lnkForgot: string;
  btnSubmit: string;
  modalTitle: string;
  modalDesc: string;
  modalClose: string;
  langBtn: string;
  userShort: string;
  userSuccess: string;
  passShort: string;
  passWeak: string;
  passSuccess: string;
}

const translations: Record<'en' | 'de', TranslationSet> = {
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

export const Login: React.FC = () => {
  // =========================================================================
  // STATE MANAGEMENT
  // =========================================================================
  const [currentLang, setCurrentLang] = useState<'en' | 'de'>('en');
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLockedOut, setIsLockedOut] = useState<boolean>(false);
  const [globalError, setGlobalError] = useState<string | null>(null);
  
  // Custom Dynamic Glow Color State (maps to --glow-color variable)
  const [glowColor, setGlowColor] = useState<string>('rgba(59, 130, 246, 0.12)');
  const [shouldShake, setShouldShake] = useState<boolean>(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Validation feedback sub-states
  const [userValidation, setUserValidation] = useState<{ status: 'idle' | 'success' | 'error'; message: string }>({ status: 'idle', message: '' });
  const [passValidation, setPassValidation] = useState<{ status: 'idle' | 'success' | 'error'; message: string }>({ status: 'idle', message: '' });

  // Evaluation Regex definitions matching original specs
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const usernameRegex = /^[a-zA-Z0-9_.-]{3,50}$/;
  const hasUpper = /[A-Z]/;
  const hasLower = /[a-z]/;
  const hasDigit = /[0-9]/;
  const hasSpecial = /[^A-Za-z0-9]/;

  const t = translations[currentLang];

  // =========================================================================
  // EFFECTS: ADAPTIVE REAL-TIME INPUT VALIDATION & GLOW SHIFTING
  // =========================================================================
  useEffect(() => {
    if (isLockedOut) return;

    let isUserValid = false;
    let isPassValid = false;

    // Evaluate Username / Corporate Email structure
    if (username === "") {
      setUserValidation({ status: 'idle', message: '' });
    } else if (username.length < 5) {
      setUserValidation({ status: 'error', message: t.userShort });
    } else if (emailRegex.test(username) || usernameRegex.test(username)) {
      setUserValidation({ status: 'success', message: t.userSuccess });
      isUserValid = true;
    } else {
      setUserValidation({ status: 'error', message: t.userShort });
    }

    // Evaluate Password Cryptographic Guidelines
    if (password === "") {
      setPassValidation({ status: 'idle', message: '' });
    } else if (password.length < 4) {
      setPassValidation({ status: 'error', message: t.passShort });
    } else if (!(hasUpper.test(password) && hasLower.test(password) && hasDigit.test(password) && hasSpecial.test(password))) {
      setPassValidation({ status: 'error', message: t.passWeak });
    } else {
      setPassValidation({ status: 'success', message: t.passSuccess });
      isPassValid = true;
    }

    // Adapt the glowing feedback color aura depending on input state safety
    if (username !== "" || password !== "") {
      if (isUserValid && isPassValid) {
        setGlowColor('rgba(16, 185, 129, 0.25)'); // Safe Emerald Glow
      } else if ((!isUserValid && username.length >= 5) || (!isPassValid && password.length >= 4)) {
        setGlowColor('rgba(239, 68, 68, 0.2)'); // Warning Red Glow
      } else {
        setGlowColor('rgba(59, 130, 246, 0.2)'); // Neutral Blue Glow
      }
    } else {
      setGlowColor('rgba(59, 130, 246, 0.12)'); // Idle Glow
    }
  }, [username, password, currentLang, isLockedOut]);

  // =========================================================================
  // EVENT HANDLERS
  // =========================================================================
  const toggleLanguage = () => {
    setCurrentLang((prev) => (prev === 'en' ? 'de' : 'en'));
  };

  const isFormValid = () => {
    const isUserValid = username.length >= 5 && (emailRegex.test(username) || usernameRegex.test(username));
    const isPassValid = password.length >= 4 && hasUpper.test(password) && hasLower.test(password) && hasDigit.test(password) && hasSpecial.test(password);
    return isUserValid && isPassValid && !isLockedOut;
  };

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLockedOut || !isFormValid()) return;

    setGlobalError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok && data.token) {
        localStorage.setItem('monitor_jwt_token', data.token);
        window.location.href = '/';
      } else {
        // Trigger structural shake feedback vector
        setShouldShake(true);
        setTimeout(() => setShouldShake(false), 400);

        setGlobalError(data.error || (currentLang === 'en' ? 'Authentication Failed' : 'Authentifizierung fehlgeschlagen'));

        // Handle Brute-Force lockout signal vector (HTTP Status 423)
        if (response.status === 423) {
          setIsLockedOut(true);
          setGlowColor('rgba(239, 68, 68, 0.4)'); // Heavy Red Lockdown Glow
        }
      }
    } catch (error) {
      setGlobalError(currentLang === 'en' ? 'Core network infrastructure fault.' : 'Verbindungsfehler zum Server infrastructure.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen w-full bg-[#0f172a] flex items-center justify-center p-4 relative overflow-hidden" 
      style={{ background: 'radial-gradient(circle at center, #1e293b 0%, #0f172a 100%)' }}
    >
      {/* Floating Language Switcher Component */}
      <LangSwitcher currentLang={currentLang} onToggle={toggleLanguage} />

      {/* Main Glassmorphic Interactive Login Card */}
      <div 
        id="main-login-card"
        style={{ boxShadow: `0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px ${glowColor}` }}
        className={`w-full max-w-[460px] bg-slate-800/70 backdrop-blur-lg border border-white/10 rounded-[24px] p-8 md:p-12 text-center relative transition-all duration-500 transform ${
          shouldShake ? 'animate-[shake_0.4s_ease-in-out]' : ''
        }`}
      >
        {/* Security Brand Emblem */}
        <div className="text-4xl mb-4 inline-block bg-gradient-to-r from-blue-500 to-blue-400 bg-clip-text text-transparent">
          <i className="bi bi-shield-lock-fill"></i>
        </div>
        <h4 id="title-main" className="text-xl font-bold text-white mb-1">{t.titleMain}</h4>
        <p id="title-sub" className="text-xs text-slate-400 mb-8">{t.titleSub}</p>

        {/* System Global Feedback Banner */}
        {globalError && (
          <div 
            id="global-alert" 
            className="mb-4 p-3 rounded-lg text-start text-xs border-0 bg-red-500/15 text-red-400 animate-fadeIn"
            role="alert"
          >
            {globalError}
          </div>
        )}

        {/* Administrative Access Form */}
        <form id="login-form" onSubmit={handleLoginSubmit} className="text-start">
          
          {/* Username Input Field Block */}
          <div className="mb-4">
            <label id="lbl-username" htmlFor="username" className="block text-xs font-medium text-slate-400 mb-2">
              {t.lblUsername}
            </label>
            <input 
              type="text" 
              id="username" 
              disabled={isLockedOut || isLoading}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#0f172a]/60 text-white border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 focus:bg-[#0f172a]/90 transition-all disabled:opacity-50"
              autoComplete="off" 
              required 
            />
            {/* Contextual Validation Feedback */}
            <ValidationMessage status={userValidation.status} message={userValidation.message} />
          </div>

          {/* Password Input Field Block */}
          <div className="mb-6">
            <label id="lbl-password" htmlFor="password" className="block text-xs font-medium text-slate-400 mb-2">
              {t.lblPassword}
            </label>
            <div className="password-container relative">
              <input 
                type={showPassword ? "text" : "password"} 
                id="password" 
                disabled={isLockedOut || isLoading}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0f172a]/60 text-white border border-white/10 rounded-xl px-4 py-3 pr-12 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 focus:bg-[#0f172a]/90 transition-all disabled:opacity-50"
                required 
              />
              <button 
                type="button" 
                id="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
                className="password-toggle absolute right-4 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                aria-label="Toggle password visibility"
              >
                <i id="toggle-icon" className={`bi ${showPassword ? 'bi-eye' : 'bi-eye-slash'}`}></i>
              </button>
            </div>
            {/* Contextual Validation Feedback */}
            <ValidationMessage status={passValidation.status} message={passValidation.message} />
          </div>

          {/* Authorization Trigger Button Node */}
          <button 
            type="submit" 
            id="submit-btn" 
            disabled={!isFormValid() || isLoading}
            className="btn btn-primary w-full bg-gradient-to-r from-blue-500 to-blue-600 disabled:from-slate-700 disabled:to-slate-700 text-white rounded-xl py-3.5 font-semibold tracking-wide hover:shadow-[0_4px_16px_rgba(59,130,246,0.35)] disabled:hover:shadow-none hover:-translate-y-[1px] active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          >
            <span id="btn-text">
              {isLockedOut 
                ? (currentLang === 'en' ? "PORTAL LOCKED" : "PORTAL GESPERRT") 
                : isLoading 
                  ? (currentLang === 'en' ? "Authenticating..." : "Authentifizierung...") 
                  : t.btnSubmit
              }
            </span>
            {isLoading && (
              <span id="btn-spinner" className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" role="status"></span>
            )}
          </button>

          {/* Password Recovery Trigger Box */}
          <div className="forgot-block-container mt-5">
            <button 
              type="button"
              id="lnk-forgot"
              onClick={() => setIsModalOpen(true)}
              className="forgot-link-box w-full block bg-white/[0.03] border border-white/[0.05] rounded-xl py-3 text-slate-400 hover:text-blue-500 hover:bg-blue-500/10 hover:border-blue-500/25 transition-all duration-250 text-xs font-medium cursor-pointer"
            >
              {t.lnkForgot}
            </button>
          </div>
        </form>
      </div>

      {/* Translucent Password Recovery Modal */}
      <RecoveryModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        translations={{
          modalTitle: t.modalTitle,
          modalDesc: t.modalDesc,
          modalClose: t.modalClose
        }}
      />
    </div>
  );
};