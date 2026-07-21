import React from 'react';

interface LoginFooterProps {
  lnkForgot: string;
  onOpenModal: () => void;
}

export const LoginFooter: React.FC<LoginFooterProps> = ({ lnkForgot, onOpenModal }) => {
  return (
    <div className="forgot-block-container pt-6 mt-6 border-t border-slate-800">
      <button
        type="button"
        id="lnk-forgot"
        onClick={onOpenModal}
        className="forgot-link-box w-full block bg-slate-800/40 border border-slate-700/60 rounded-xl py-3 text-slate-300 hover:text-white hover:bg-blue-600/20 hover:border-blue-500/40 transition-all duration-300 text-xs font-semibold tracking-wide cursor-pointer shadow-sm"
      >
        {lnkForgot}
      </button>
    </div>
  );
};