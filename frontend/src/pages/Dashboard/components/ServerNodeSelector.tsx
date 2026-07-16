import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR SERVER NODES
// =========================================================================
export type ServerNodeKey = 'Docker_Production_Container' | 'Windows_Host' | 'VMware_Ubuntu';

interface ServerNodeSelectorProps {
  /** The actively inspected server node key used in state context matching */
  activeNode: ServerNodeKey;
  /** Action trigger executed when a different server infrastructure node is selected */
  onNodeChange: (node: ServerNodeKey) => void;
  /** The high-contrast text description of the currently selected node (e.g., Node: Docker Node (Ludwigshafen)) */
  nodeDisplayLabel: string;
  /** 
   * Active node system status color signature for the live heartbeat component:
   * - 'red': Blinking crimson pulse (Docker Node)
   * - 'blue': Blinking azure pulse (Windows Host)
   * - 'green': Blinking emerald pulse (VMware Linux)
   * - 'offline': Static critical warning signifier 
   */
  heartbeatState: 'red' | 'blue' | 'green' | 'offline';
}

/**
 * ServerNodeSelector Component
 * 
 * Renders the top-level sub-navigation node tabs and the contextual
 * live system heartbeat indicators. Retains precise metadata, data attributes, 
 * and absolute CSS transition guidelines matching your database structures.
 */
export const ServerNodeSelector: React.FC<ServerNodeSelectorProps> = ({
  activeNode,
  onNodeChange,
  nodeDisplayLabel,
  heartbeatState,
}) => {
  // Translate our custom states to their corresponding heartbeat pulse animations
  const getHeartbeatClasses = () => {
    switch (heartbeatState) {
      case 'red':
        return 'bg-red-500 shadow-[0_0_8px_#ef4444] animate-[blink-red_1.5s_infinite_ease-in-out]';
      case 'blue':
        return 'bg-blue-500 shadow-[0_0_8px_#3b82f6] animate-[blink-blue_1.5s_infinite_ease-in-out]';
      case 'green':
        return 'bg-emerald-500 shadow-[0_0_8px_#22c55e] animate-[blink-green_1.5s_infinite_ease-in-out]';
      case 'offline':
      default:
        return 'bg-red-500 shadow-[0_0_12px_#ef4444]'; // Static critical aura on network timeout
    }
  };

  return (
    <div id="serverTabsContainer" className="mb-6 block">
      <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center border-b border-white/5 pb-3">
        
        {/* Horizontal Navigation Pills matching exact custom database IDs */}
        <ul className="flex flex-wrap gap-2 list-none p-0 m-0" id="nodeSelectorTabs" role="tablist">
          <li role="presentation">
            <button
              id="tab-docker"
              data-node="Docker_Production_Container"
              onClick={() => onNodeChange('Docker_Production_Container')}
              type="button"
              role="tab"
              className={`border border-transparent rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-250 cursor-pointer flex items-center gap-2 ${
                activeNode === 'Docker_Production_Container'
                  ? 'text-white bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.25)]'
                  : 'text-slate-400 bg-white/[0.02] hover:text-white hover:bg-white/[0.06] hover:border-white/5'
              }`}
            >
              <i className="fab fa-docker text-base"></i>
              <span>Docker Node</span>
            </button>
          </li>
          
          <li role="presentation">
            <button
              id="tab-windows"
              data-node="Windows_Host"
              onClick={() => onNodeChange('Windows_Host')}
              type="button"
              role="tab"
              className={`border border-transparent rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-250 cursor-pointer flex items-center gap-2 ${
                activeNode === 'Windows_Host'
                  ? 'text-white bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.25)]'
                  : 'text-slate-400 bg-white/[0.02] hover:text-white hover:bg-white/[0.06] hover:border-white/5'
              }`}
            >
              <i className="fab fa-windows text-base"></i>
              <span>Windows Host</span>
            </button>
          </li>
          
          <li role="presentation">
            <button
              id="tab-vmware"
              data-node="VMware_Ubuntu"
              onClick={() => onNodeChange('VMware_Ubuntu')}
              type="button"
              role="tab"
              className={`border border-transparent rounded-xl px-4 py-2 text-sm font-semibold transition-all duration-250 cursor-pointer flex items-center gap-2 ${
                activeNode === 'VMware_Ubuntu'
                  ? 'text-white bg-gradient-to-br from-blue-500/20 to-blue-600/20 border-blue-500/40 shadow-[0_0_15px_rgba(59,130,246,0.25)]'
                  : 'text-slate-400 bg-white/[0.02] hover:text-white hover:bg-white/[0.06] hover:border-white/5'
              }`}
            >
              <i className="fab fa-linux text-base"></i>
              <span>VMware Linux</span>
            </button>
          </li>
        </ul>

        {/* Live Active Server Node Identification Header & Pulsing Node status indicator */}
        <div className="flex items-center gap-3 bg-white/[0.02] border border-white/5 rounded-xl px-3.5 py-1.5 self-stretch sm:self-auto justify-between">
          <span 
            className="text-xs text-slate-400 font-mono tracking-wider" 
            id="currentNodeDisplay"
          >
            {nodeDisplayLabel}
          </span>
          <div 
            id="nodeHeartbeatIndicator" 
            className={`w-2.5 h-2.5 rounded-full transition-all duration-400 ease-in-out ${getHeartbeatClasses()}`}
          />
        </div>

      </div>
    </div>
  );
};