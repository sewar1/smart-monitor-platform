import React from 'react';

interface LoginCardProps {
  glowColor: string;
  shouldShake: boolean;
  children: React.ReactNode;
}

export const LoginCard: React.FC<LoginCardProps> = ({ glowColor, shouldShake, children }) => {
  return (
    <div
      id="main-login-card"
      style={{ boxShadow: `0 25px 60px rgba(0, 0, 0, 0.8), 0 0 50px ${glowColor}` }}
      className={`w-full max-w-[480px] min-h-[620px] bg-[#111827]/95 border border-slate-700/80 rounded-[28px] p-10 flex flex-col justify-between relative transition-all duration-500 transform hover:scale-[1.01] ${
        shouldShake ? 'animate-shake' : ''
      }`}
    >
      {children}
    </div>
  );
};