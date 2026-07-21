import React from 'react';

interface LoginLayoutProps {
  children: React.ReactNode;
}

export const LoginLayout: React.FC<LoginLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen w-full bg-[#0b0f19] flex items-center justify-center p-6 relative font-sans antialiased overflow-hidden">
      {children}
    </div>
  );
};