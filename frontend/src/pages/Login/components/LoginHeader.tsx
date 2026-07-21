import React from 'react';

interface LoginHeaderProps {
  titleMain: string;
  titleSub: string;
}

export const LoginHeader: React.FC<LoginHeaderProps> = ({ titleMain, titleSub }) => {
  return (
    <div className="text-center">
      <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 text-2xl shadow-lg shadow-blue-500/10">
        <i className="bi bi-shield-lock-fill"></i>
      </div>
      <h4 id="title-main" className="text-2xl font-bold text-white tracking-tight mb-1">{titleMain}</h4>
      <p id="title-sub" className="text-xs text-slate-400 font-medium tracking-wider uppercase">{titleSub}</p>
    </div>
  );
};