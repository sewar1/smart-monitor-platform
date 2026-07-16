import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR METRICS GRID PROPS
// =========================================================================
interface MetricsGridProps {
  /** CPU utilization percentage (0 to 100) */
  cpuValue: number;
  /** RAM usage percentage (0 to 100) */
  ramValue: number;
  /** Disk storage utilization percentage (0 to 100) */
  diskValue: number;
  /** Overall weighted health matrix index score (e.g., 0 to 100) */
  healthScore: number;
  /** High-contrast semantic status label for system integrity (e.g., "Analyzing Matrix", "HEALTHY", "CRITICAL") */
  healthStatusText: string;
  /** 
   * Dynamic CSS color representation of the health state:
   * - 'healthy': Emerald green theme
   * - 'warning': Amber amber theme
   * - 'critical': Crimson red theme
   */
  healthStatusSeverity: 'healthy' | 'warning' | 'critical';
  /** Preserved structured localization labels and context mappings */
  translations: {
    lblCpu: string;
    lblRam: string;
    lblDisk: string;
    lblMatrix: string;
  };
}

/**
 * MetricsGrid Component
 * 
 * Renders the top-tier resource telemetry widgets layout.
 * Translates traditional Bootstrap row/col scaffolding into responsive Tailwind Grid utilities.
 * Keeps exact original DOM IDs for data-binding automation:
 * 'cpu', 'cpu-bar', 'ram', 'ram-bar', 'disk', 'disk-bar', 'health-score', 'health-status'.
 */
export const MetricsGrid: React.FC<MetricsGridProps> = ({
  cpuValue,
  ramValue,
  diskValue,
  healthScore,
  healthStatusText,
  healthStatusSeverity,
  translations,
}) => {
  
  // Calculate dynamic colors for status badges based on severity
  const getSeverityBadgeClasses = () => {
    switch (healthStatusSeverity) {
      case 'healthy':
        return 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20';
      case 'warning':
        return 'bg-amber-500/10 text-amber-400 border border-amber-500/20';
      case 'critical':
        return 'bg-rose-500/10 text-rose-400 border border-rose-500/20';
      default:
        return 'bg-slate-500/10 text-slate-400 border border-slate-500/20';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-6">
      
      {/* 1. Processor Load (CPU) Card */}
      <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:-translate-y-1 hover:border-white/15 transition-all duration-300 ease-out">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block" id="lbl-cpu">
              {translations.lblCpu}
            </span>
            <div className="text-3xl font-extrabold mt-1 text-white" id="cpu">
              {cpuValue}%
            </div>
          </div>
          <div className="text-2xl p-3 rounded-xl bg-white/[0.04] flex items-center justify-center text-rose-500 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
            <i className="fa-solid fa-microchip"></i>
          </div>
        </div>
        <div className="bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
          <div 
            id="cpu-bar" 
            className="h-full bg-rose-500 transition-all duration-500 ease-out" 
            role="progressbar"
            style={{ width: `${cpuValue}%` }}
          />
        </div>
      </div>

      {/* 2. Memory Pools (RAM) Card */}
      <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:-translate-y-1 hover:border-white/15 transition-all duration-300 ease-out">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block" id="lbl-ram">
              {translations.lblRam}
            </span>
            <div className="text-3xl font-extrabold mt-1 text-white" id="ram">
              {ramValue}%
            </div>
          </div>
          <div className="text-2xl p-3 rounded-xl bg-white/[0.04] flex items-center justify-center text-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.15)]">
            <i className="fa-solid fa-memory"></i>
          </div>
        </div>
        <div className="bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
          <div 
            id="ram-bar" 
            className="h-full bg-blue-500 transition-all duration-500 ease-out" 
            role="progressbar"
            style={{ width: `${ramValue}%` }}
          />
        </div>
      </div>

      {/* 3. Storage Block (DISK) Card */}
      <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:-translate-y-1 hover:border-white/15 transition-all duration-300 ease-out">
        <div className="flex justify-between items-center">
          <div>
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block" id="lbl-disk">
              {translations.lblDisk}
            </span>
            <div className="text-3xl font-extrabold mt-1 text-white" id="disk">
              {diskValue}%
            </div>
          </div>
          <div className="text-2xl p-3 rounded-xl bg-white/[0.04] flex items-center justify-center text-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.15)]">
            <i className="fa-solid fa-hard-drive"></i>
          </div>
        </div>
        <div className="bg-slate-800 h-1.5 rounded-full mt-4 overflow-hidden">
          <div 
            id="disk-bar" 
            className="h-full bg-emerald-500 transition-all duration-500 ease-out" 
            role="progressbar"
            style={{ width: `${diskValue}%` }}
          />
        </div>
      </div>

      {/* 4. Weighted Health Matrix Card */}
      <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:-translate-y-1 hover:border-white/15 transition-all duration-300 ease-out text-center flex flex-col justify-center items-center">
        <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider block" id="lbl-matrix">
          {translations.lblMatrix}
        </span>
        <div className="text-[38px] font-extrabold mt-2 text-white leading-none" id="health-score">
          {healthScore}
        </div>
        <span 
          id="health-status" 
          className={`text-[11px] font-bold px-3 py-1 rounded-full mt-3 inline-block tracking-wide uppercase ${getSeverityBadgeClasses()}`}
        >
          {healthStatusText}
        </span>
      </div>

    </div>
  );
};