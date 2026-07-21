import React from 'react';
import type { ValidationState, LanguageCode } from '../types/login.types';
import { UsernameField } from './UsernameField';
import { PasswordField } from './PasswordField';
import { SubmitButton } from './SubmitButton';

interface LoginFormProps {
  username: string;
  onUsernameChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  userValidation: ValidationState;
  password: string;
  onPasswordChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  passValidation: ValidationState;
  showPassword: boolean;
  onToggleShowPassword: () => void;
  isLockedOut: boolean;
  isLoading: boolean;
  isFormValid: boolean;
  currentLang: LanguageCode;
  submitButtonText: string;
  onSubmit: (e: React.FormEvent) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  username,
  onUsernameChange,
  userValidation,
  password,
  onPasswordChange,
  passValidation,
  showPassword,
  onToggleShowPassword,
  isLockedOut,
  isLoading,
  isFormValid,
  currentLang,
  submitButtonText,
  onSubmit,
}) => {
  return (
    <form id="login-form" onSubmit={onSubmit} className="space-y-6">
      <UsernameField
        label={currentLang === 'en' ? "Username or Corporate Email" : "Benutzername oder Firmen-E-Mail"}
        value={username}
        onChange={onUsernameChange}
        disabled={isLockedOut || isLoading}
        validation={userValidation}
      />

      <PasswordField
        label={currentLang === 'en' ? "Password" : "Passwort"}
        value={password}
        onChange={onPasswordChange}
        disabled={isLockedOut || isLoading}
        showPassword={showPassword}
        onToggleShow={onToggleShowPassword}
        validation={passValidation}
      />

      <SubmitButton
        isValid={isFormValid}
        isLoading={isLoading}
        isLockedOut={isLockedOut}
        currentLang={currentLang}
        text={submitButtonText}
      />
    </form>
  );
};