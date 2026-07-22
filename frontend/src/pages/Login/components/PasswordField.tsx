import React from 'react';
import type { ValidationState } from '../types/login.types';
import { ValidationMessage } from './ValidationMessage';

interface PasswordFieldProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled: boolean;
  showPassword: boolean;
  onToggleShow: () => void;
  validation: ValidationState;
}

export const PasswordField: React.FC<PasswordFieldProps> = ({
  label,
  value,
  onChange,
  disabled,
  showPassword,
  onToggleShow,
  validation,
}) => {
  return (
    <div className="space-y-2 text-start">
      <label id="lbl-password" htmlFor="password" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
        {label}
      </label>
      <div className="relative">
        <input
          type={showPassword ? "text" : "password"}
          id="password"
          disabled={disabled}
          value={value}
          onChange={onChange}
          className="w-full bg-[#0b0f19] text-white placeholder-slate-600 border border-slate-700 rounded-xl px-4 py-3 pr-12 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all duration-200 disabled:opacity-50 shadow-inner"
          required
        />
        <button
          type="button"
          id="password-toggle-btn"
          onClick={onToggleShow}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-300 hover:text-white transition-colors cursor-pointer p-1"
          aria-label="Toggle password visibility"
        >
          <i id="toggle-icon" className={`bi ${showPassword ? 'bi-eye' : 'bi-eye-slash'} text-lg text-slate-300 hover:text-cyan-400`}></i>
        </button>
      </div>
      <ValidationMessage status={validation.status} message={validation.message} />
    </div>
  );
};