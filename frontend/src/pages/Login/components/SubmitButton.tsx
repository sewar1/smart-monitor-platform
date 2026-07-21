import React from 'react';
import type { LanguageCode } from '../types/login.types';

interface SubmitButtonProps {
  isValid: boolean;
  isLoading: boolean;
  isLockedOut: boolean;
  currentLang: LanguageCode;
  text: string;
}

export const SubmitButton: React.FC<SubmitButtonProps> = ({ isValid, isLoading, isLockedOut, currentLang, text }) => {
  return (
    <button
      type="submit"
      id="submit-btn"
      disabled={!isValid || isLoading}
      className="w-full mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 text-white font-semibold rounded-xl py-3.5 text-sm tracking-wide transition-all duration-200 flex items-center justify-center gap-2 cursor-pointer disabled:cursor-not-allowed shadow-lg shadow-blue-600/30 hover:shadow-blue-500/50 hover:-translate-y-0.5 active:translate-y-0"
    >
      <span id="btn-text">
        {isLockedOut
          ? (currentLang === 'en' ? "PORTAL LOCKED" : "PORTAL GESPERRT")
          : isLoading
            ? (currentLang === 'en' ? "Authenticating..." : "Authentifizierung...")
            : text}
      </span>
      {isLoading && (
        <span id="btn-spinner" className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" role="status"></span>
      )}
    </button>
  );
};