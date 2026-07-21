import React from 'react';
import type { LanguageCode } from '../types/login.types';

interface LangSwitcherProps {
  currentLang: LanguageCode;
  onToggle: () => void;
}

export const LangSwitcher: React.FC<LangSwitcherProps> = ({ currentLang, onToggle }) => {
  return (
    <button
      type="button"
      id="lang-btn"
      onClick={onToggle}
      className="bg-white/5 border border-white/10 text-slate-300 rounded-lg px-3 py-1.5 text-xs font-semibold hover:bg-white/10 hover:text-white transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50 shadow-sm"
    >
      {currentLang === 'en' ? 'DE' : 'EN'}
    </button>
  );
};