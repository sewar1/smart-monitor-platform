import React from 'react';

// =========================================================================
// TYPES & INTERFACES FOR RECOVERYMODAL PROPS
// =========================================================================
interface RecoveryModalProps {
  /** Controller flag to determine whether the portal modal is visible */
  isOpen: boolean;
  /** Action trigger to handle the closing and destruction of the modal overlay */
  onClose: () => void;
  /** Structured localization mapping data containing key-value translation pairs */
  translations: {
    modalTitle: string;
    modalDesc: string;
    modalClose: string;
  };
}

/**
 * RecoveryModal Component
 * 
 * Renders a premium, translucent DevSecOps password recovery portal overlay.
 * Replaces traditional Bootstrap-dependent modal events with fully managed React states.
 * Guarantees visual consistency, alignment, and semantic HTML representation.
 */
export const RecoveryModal: React.FC<RecoveryModalProps> = ({
  isOpen,
  onClose,
  translations,
}) => {
  // If the modal is not flag-triggered to open, prevent rendering to clean up DOM
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      {/* Premium Dark Glassmorphic Card Container */}
      <div 
        className="bg-slate-800 border border-slate-700/80 rounded-[20px] max-w-md w-full p-6 shadow-2xl relative animate-scaleUp"
        onClick={(e) => e.stopPropagation()} // Stop click propagation to avoid closing on inner clicks
      >
        {/* Header Block with Dismissal Trigger Button */}
        <div className="flex justify-between items-start mb-4">
          <h6 
            id="modal-title" 
            className="text-white font-bold text-base tracking-wide"
          >
            {translations.modalTitle}
          </h6>
          <button 
            type="button" 
            onClick={onClose}
            className="text-slate-400 hover:text-white transition-colors cursor-pointer focus:outline-none"
            aria-label="Close"
          >
            <i className="bi bi-x-lg text-lg"></i>
          </button>
        </div>

        {/* Content Body containing Administrative recovery guidelines */}
        <div className="mb-6">
          <p 
            id="modal-desc" 
            className="text-slate-400 text-xs leading-relaxed font-medium"
          >
            {translations.modalDesc}
          </p>
        </div>

        {/* Footer Actions area containing Close triggers */}
        <div className="flex justify-end border-0">
          <button 
            type="button" 
            id="modal-close"
            onClick={onClose}
            className="bg-slate-700 hover:bg-slate-650 text-white rounded-lg px-4 py-2 text-xs font-semibold transition-all cursor-pointer focus:outline-none focus:ring-2 focus:ring-slate-500"
          >
            {translations.modalClose}
          </button>
        </div>
      </div>
    </div>
  );
};