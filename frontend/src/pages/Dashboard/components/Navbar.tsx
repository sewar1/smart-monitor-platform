import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR NAVBAR PROPS
// =========================================================================
interface NavbarProps {
  /** The currently selected major application tab ('telemetry' | 'directory') */
  activeTab: 'telemetry' | 'directory';
  /** Event trigger callback executed when a top tab item selection transitions */
  onTabChange: (tab: 'telemetry' | 'directory') => void;
  /** Current localization configuration state ('en' or 'de') */
  currentLang: 'en' | 'de';
  /** Action trigger to toggle globally mapped language contexts */
  onToggleLanguage: () => void;
  /** Direct callback to initiate safe and audited session destruction */
  onLogout: () => void;
  /** Preserved structured localization labels and context mappings */
  translations: {
    navTitle: string;
    tabTelemetry: string;
    tabDirectory: string;
    langBtn: string;
  };
}

/**
 * Navbar Component
 * 
 * Implements a glassmorphic top navigation portal container.
 * Fully preserves precise original IDs and styling benchmarks for frictionless integration.
 */
export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  onTabChange,
  currentLang,
  onToggleLanguage,
  onLogout,
  translations,
}) => {
  return (
    <nav className="bg-[#0f172a]/60 backdrop-blur-md border-b border-white/5 py-4 px-8 shadow-[0_4px_30px_rgba(0,0,0,0.4)] flex justify-between items-center">
      <div className="container-fluid flex justify-between items-center w-full">
        {/* Brand/Platform Logo Node */}
        <span className="text-xl font-extrabold tracking-wider text-white flex items-center gap-3">
          <i className="fa-solid fa-shield-halved text-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.5)]"></i>
          <span id="nav-title">{translations.navTitle}</span>
          <span className="bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-semibold px-2 py-1 rounded-md">
            v2.0-Cluster
          </span>
        </span>

        {/* Tab Routing Controller Area */}
        <ul className="flex border-none gap-2 m-0 p-0 list-none" id="dashboardTabs" role="tablist">
          <li role="presentation">
            <button
              id="telemetry-tab"
              onClick={() => onTabChange('telemetry')}
              type="button"
              role="tab"
              className={`border border-transparent rounded-xl px-5 py-2.5 font-semibold text-sm transition-all duration-300 cursor-pointer flex items-center gap-2 ${
                activeTab === 'telemetry'
                  ? 'text-white bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.25)]'
                  : 'text-slate-400 bg-white/[0.02] hover:text-white hover:bg-white/[0.06] hover:border-white/5'
              }`}
            >
              <i className="fa-solid fa-chart-line"></i>
              <span id="tab-telemetry">{translations.tabTelemetry}</span>
            </button>
          </li>
          <li role="presentation">
            <button
              id="directory-tab"
              onClick={() => onTabChange('directory')}
              type="button"
              role="tab"
              className={`border border-transparent rounded-xl px-5 py-2.5 font-semibold text-sm transition-all duration-300 cursor-pointer flex items-center gap-2 ${
                activeTab === 'directory'
                  ? 'text-white bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.25)]'
                  : 'text-slate-400 bg-white/[0.02] hover:text-white hover:bg-white/[0.06] hover:border-white/5'
              }`}
            >
              <i className="fa-solid fa-users-gear"></i>
              <span id="tab-directory">{translations.tabDirectory}</span>
            </button>
          </li>
        </ul>

        {/* Language switcher & secure exit gateways */}
        <div className="flex gap-2.5 items-center">
          <button
            type="button"
            id="lang-btn"
            onClick={onToggleLanguage}
            className="bg-white/5 border border-white/10 text-slate-400 rounded-lg px-3 py-2 text-xs font-semibold hover:bg-white/10 hover:text-white transition-all cursor-pointer flex items-center gap-2"
          >
            <i className="fa-solid fa-language text-sm"></i>
            {currentLang === 'en' ? 'DE' : 'EN'}
          </button>
          <button
            type="button"
            onClick={onLogout}
            className="border border-red-500/20 text-red-400 bg-red-500/5 hover:bg-red-500/10 hover:text-red-300 rounded-lg px-3.5 py-2 text-xs transition-all cursor-pointer flex items-center justify-center h-[38px] focus:outline-none"
            aria-label="Secure Logout Vector"
          >
            <i className="fa-solid fa-power-off"></i>
          </button>
        </div>
      </div>
    </nav>
  );
};