import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR LANGSWITCHER PROPS
// =========================================================================
interface LangSwitcherProps {
  /** The currently active language context code ('en' or 'de') */
  currentLang: 'en' | 'de';
  /** Callback trigger event to switch global translation contexts */
  onToggle: () => void;
}

/**
 * LangSwitcher Component
 * Renders the floating premium glassmorphic language toggling controller.
 * Designed to preserve identical aesthetics and absolute positioning matrixes.
 */
export const LangSwitcher: React.FC<LangSwitcherProps> = ({ currentLang, onToggle }) => {
  return (
    <div className="absolute top-6 right-6 z-10">
      <button
        type="button"
        id="lang-btn"
        onClick={onToggle}
        className="bg-white/5 border border-white/10 text-slate-400 rounded-lg px-2.5 py-1 text-xs font-semibold hover:bg-white/10 hover:text-white transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-blue-500/50"
      >
        {/* Dynamic target language projection: If current is 'en', show 'DE' as action */}
        {currentLang === 'en' ? 'DE' : 'EN'}
      </button>
    </div>
  );
};