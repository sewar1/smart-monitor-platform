import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR PROCESS TABLE DATA & EVENTS
// =========================================================================
export interface SystemProcess {
  id: string | number;
  descriptor: string;
  metricValue: string | number;
}

export interface IncidentLog {
  id: string | number;
  message: string;
  timestamp?: string;
  type?: 'healthy' | 'warning' | 'critical';
}

interface TelemetryPanelsProps {
  /** Controller flag to completely show/hide this pane based on major active tabs */
  isVisible: boolean;
  /** Active Live Incident logs rendered directly in the incident console view */
  activeIncidents: IncidentLog[];
  /** Historical archived logs displayed in the persistent chronological log ledger */
  archivedIncidents: IncidentLog[];
  /** List of processes consuming the most CPU threads */
  cpuProcesses: SystemProcess[];
  /** List of processes utilizing the most memory pages */
  ramProcesses: SystemProcess[];
  /** React ref bound directly to the HTML5 Canvas node for Chart.js rendering context */
  canvasRef: React.RefObject<HTMLCanvasElement | null>;
  /** Preserved structured localization labels and context mappings */
  translations: {
    hdrIncidents: string;
    hdrCpuThreads: string;
    hdrRamPages: string;
    hdrLedger: string;
    hdrChart: string;
    thCpuDesc: string;
    thCpuLoad: string;
    thRamDesc: string;
    thRamBase: string;
    lblOperationalNormal: string;
    lblWaitingHistory: string;
  };
}

/**
 * TelemetryPanels Component
 * 
 * Houses the real-time activity consoles, resource ranking tables, historical ledger,
 * and the HTML5 canvas workspace designated for Chart.js stream wave analyzers.
 * Preserves all original DOM IDs and class names for dynamic script updates.
 */
export const TelemetryPanels: React.FC<TelemetryPanelsProps> = ({
  isVisible,
  activeIncidents,
  archivedIncidents,
  cpuProcesses,
  ramProcesses,
  canvasRef,
  translations,
}) => {
  // If this panel is not active in the master routing state, restrict rendering
  if (!isVisible) return null;

  return (
    <div id="telemetry-pane" className="animate-fadeIn">
      
      {/* Real-time Incident Console & Performance Resource Logs Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        
        {/* 1. Active Incident Console */}
        <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
          <h4 id="hdr-incidents" className="text-sm font-bold text-white mb-5 flex items-center gap-2.5">
            <i className="fa-solid fa-bell-slash text-amber-500"></i>
            {translations.hdrIncidents}
          </h4>
          <div 
            id="alerts-container" 
            className="max-h-[250px] overflow-y-auto font-mono text-xs pr-2 space-y-2 scrollbar-thin"
          >
            {activeIncidents.length === 0 ? (
              <p className="text-emerald-400 flex items-center gap-2">
                <i className="fa-solid fa-circle-check"></i> 
                {translations.lblOperationalNormal}
              </p>
            ) : (
              activeIncidents.map((incident) => (
                <div 
                  key={incident.id} 
                  className="p-2.5 bg-white/[0.02] border-l-3 border-amber-500 rounded-r-lg text-slate-300 leading-relaxed"
                >
                  {incident.timestamp && <span className="text-[10px] text-slate-500 mr-1">[{incident.timestamp}]</span>}
                  {incident.message}
                </div>
              ))
            )}
          </div>
        </div>

        {/* 2. Top CPU Threads Profile */}
        <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
          <h4 id="hdr-cpu-threads" className="text-sm font-bold text-white mb-5 flex items-center gap-2.5">
            <i className="fa-solid fa-fire text-rose-500"></i>
            {translations.hdrCpuThreads}
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5">
                  <th id="th-cpu-desc" className="text-slate-400 text-[11px] uppercase tracking-wider py-3 font-semibold">
                    {translations.thCpuDesc}
                  </th>
                  <th id="th-cpu-load" className="text-slate-400 text-[11px] uppercase tracking-wider py-3 font-semibold text-end">
                    {translations.thCpuLoad}
                  </th>
                </tr>
              </thead>
              <tbody id="cpu-processes" className="divide-y divide-white/[0.03]">
                {cpuProcesses.map((proc) => (
                  <tr key={proc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 text-sm text-slate-200 font-medium">{proc.descriptor}</td>
                    <td className="py-3 text-sm text-slate-200 text-end font-semibold">{proc.metricValue}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* 3. Top RAM Pages Profile */}
        <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
          <h4 id="hdr-ram-pages" className="text-sm font-bold text-white mb-5 flex items-center gap-2.5">
            <i className="fa-solid fa-brain text-blue-400"></i>
            {translations.hdrRamPages}
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5">
                  <th id="th-ram-desc" className="text-slate-400 text-[11px] uppercase tracking-wider py-3 font-semibold">
                    {translations.thRamDesc}
                  </th>
                  <th id="th-ram-base" className="text-slate-400 text-[11px] uppercase tracking-wider py-3 font-semibold text-end">
                    {translations.thRamBase}
                  </th>
                </tr>
              </thead>
              <tbody id="memory-processes" className="divide-y divide-white/[0.03]">
                {ramProcesses.map((proc) => (
                  <tr key={proc.id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 text-sm text-slate-200 font-medium">{proc.descriptor}</td>
                    <td className="py-3 text-sm text-slate-200 text-end font-semibold">{proc.metricValue}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

      {/* Persistent Chronological Alert History Ledger */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
          <h4 id="hdr-ledger" className="text-sm font-bold text-white mb-5 flex items-center gap-2.5">
            <i className="fa-solid fa-database text-slate-500"></i>
            {translations.hdrLedger}
          </h4>
          <div 
            id="alert-history" 
            className="max-h-[150px] overflow-y-auto font-mono text-xs pr-2 space-y-2 scrollbar-thin"
          >
            {archivedIncidents.length === 0 ? (
              <p className="text-slate-500 flex items-center gap-2">
                <i className="fa-solid fa-circle-nodes animate-pulse"></i> 
                {translations.lblWaitingHistory}
              </p>
            ) : (
              archivedIncidents.map((archive) => (
                <div 
                  key={archive.id} 
                  className="p-2 bg-white/[0.01] border-l border-slate-700/50 text-slate-400 text-xs"
                >
                  {archive.message}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* HTML5 Canvas Telemetry Live Waveform Chart Card */}
      <div className="grid grid-cols-1 gap-6 mb-6">
        <div className="bg-slate-900/75 backdrop-blur-lg border border-white/5 rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.25)] hover:border-white/10 transition-all duration-300">
          <h4 id="hdr-chart" className="text-sm font-bold text-white mb-5 flex items-center gap-2.5">
            <i className="fa-solid fa-chart-line text-blue-500"></i>
            {translations.hdrChart}
          </h4>
          <div className="h-[40vh] relative w-full">
            <canvas id="chart" ref={canvasRef}></canvas>
          </div>
        </div>
      </div>

    </div>
  );
};