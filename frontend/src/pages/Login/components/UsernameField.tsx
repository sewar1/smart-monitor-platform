import React from 'react';
import type { ValidationState } from '../types/login.types';
import { ValidationMessage } from './ValidationMessage';

interface UsernameFieldProps {
  label: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  disabled: boolean;
  validation: ValidationState;
}

export const UsernameField: React.FC<UsernameFieldProps> = ({ label, value, onChange, disabled, validation }) => {
  return (
    <div className="space-y-2 text-start">
      <label id="lbl-username" htmlFor="username" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
        {label}
      </label>
      <input
        type="text"
        id="username"
        disabled={disabled}
        value={value}
        onChange={onChange}
        className="w-full bg-[#0b0f19] text-white placeholder-slate-600 border border-slate-700 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 transition-all duration-200 disabled:opacity-50 shadow-inner"
        autoComplete="off"
        required
      />
      <ValidationMessage status={validation.status} message={validation.message} />
    </div>
  );
};