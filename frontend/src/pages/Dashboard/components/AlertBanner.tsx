import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR ALERT BANNER PROPS
// =========================================================================
interface AlertBannerProps {
  /** Controller flag to show or completely destroy the banner layout based on active system telemetry state */
  isVisible: boolean;
  /** The localized critical message payload (e.g., CRITICAL INFRASTRUCTURE EVENT DETECTED) */
  alertText: string;
  /** The highly-precise logged timestamp string for the event (e.g., 00:00:00) */
  timestamp: string;
}

/**
 * AlertBanner Component
 * 
 * Renders a high-importance administrative alert bar.
 * Replicates the custom 'corePulse' keyframe styling using unified Tailwind classes.
 * Preserves the exact original DOM identifiers: 'alertBox', 'banner-alert-text', and 'alertTimestamp'.
 */
export const AlertBanner: React.FC<AlertBannerProps> = ({
  isVisible,
  alertText,
  timestamp,
}) => {
  // If no critical signal vector is active, do not render to clear layout memory
  if (!isVisible) return null;

  return (
    <div
      id="alertBox"
      className="bg-gradient-to-r from-red-500 to-red-800 text-white p-4 rounded-xl mb-6 font-bold shadow-[0_4px_20px_rgba(239,68,68,0.35)] animate-core-pulse"
      role="alert"
    >
      <div className="flex items-center justify-between">
        
        {/* Warning Icon and Event Description Container */}
        <div className="flex items-center gap-3">
          <i className="fa-solid fa-triangle-exclamation animate-pulse text-lg"></i>
          <span id="banner-alert-text" className="tracking-wide text-sm md:text-base">
            {alertText}
          </span>
        </div>

        {/* Dynamic Chronological Indicator */}
        <span
          id="alertTimestamp"
          className="badge bg-black/20 text-white font-mono text-xs px-2.5 py-1.5 rounded-md"
        >
          {timestamp}
        </span>

      </div>
    </div>
  );
};