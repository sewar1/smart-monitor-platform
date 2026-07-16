import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR VALIDATION MESSAGE PROPS
// =========================================================================
interface ValidationMessageProps {
  /** The direct human-readable guidance text to be rendered to the user */
  message: string;
  /** 
   * The semantic state of the validation:
   * - 'success': Indicates passed requirements (typically green styling)
   * - 'error': Indicates validation failure or pending critical action (typically red styling)
   * - 'idle': Default system guide status (gray/muted styling)
   */
  status: 'success' | 'error' | 'idle';
  /** Optional custom CSS class overrides for granular positioning or layout alignment */
  className?: string;
}

/**
 * ValidationMessage Component
 * 
 * Provides instantaneous, real-time contextual feedback on security criteria,
 * such as input patterns, format confirmations, or password complexity assessments.
 * Engineered to match the dynamic micro-interactions of the original login viewport.
 */
export const ValidationMessage: React.FC<ValidationMessageProps> = ({
  message,
  status,
  className = '',
}) => {
  // If there's no message to display, render nothing to maintain clean DOM structure
  if (!message) return null;

  // Determine dynamic styling and state signifiers depending on the evaluation status
  const getStatusStyles = () => {
    switch (status) {
      case 'success':
        return {
          textColor: 'text-emerald-400',
          iconColor: 'text-emerald-400/80',
          containerBg: 'bg-emerald-500/5 border-emerald-500/10',
          // SVG Path for an elegant validation checkmark icon
          iconPath: (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          ),
        };
      case 'error':
        return {
          textColor: 'text-rose-400',
          iconColor: 'text-rose-400/80',
          containerBg: 'bg-rose-500/5 border-rose-500/10',
          // SVG Path for a clean system error warning icon
          iconPath: (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          ),
        };
      case 'idle':
      default:
        return {
          textColor: 'text-slate-400',
          iconColor: 'text-slate-400/80',
          containerBg: 'bg-white/5 border-white/10',
          // SVG Path for an informative, neutral feedback icon
          iconPath: (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          ),
        };
    }
  };

  const { textColor, iconColor, containerBg, iconPath } = getStatusStyles();

  return (
    <div
      className={`flex items-center gap-2 px-3 py-2 mt-2 rounded-lg border text-xs leading-relaxed transition-all duration-300 animate-fadeIn ${containerBg} ${className}`}
    >
      <svg
        className={`w-4 h-4 flex-shrink-0 ${iconColor}`}
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        {iconPath}
      </svg>
      <span className={`font-medium ${textColor}`}>{message}</span>
    </div>
  );
};