import { useState, useEffect } from 'react';
import type { ValidationState, LanguageCode } from '../types/login.types';
import { translations } from '../constants/translations';
import { emailRegex, usernameRegex, hasUpper, hasLower, hasDigit, hasSpecial } from '../utils/validators';

export const useLoginValidation = (username: string, password: string, currentLang: LanguageCode, isLockedOut: boolean) => {
  const [userValidation, setUserValidation] = useState<ValidationState>({ status: 'idle', message: '' });
  const [passValidation, setPassValidation] = useState<ValidationState>({ status: 'idle', message: '' });
  const [isUserValid, setIsUserValid] = useState<boolean>(false);
  const [isPassValid, setIsPassValid] = useState<boolean>(false);

  const t = translations[currentLang];

  useEffect(() => {
    if (isLockedOut) return;

    let userValidFlag = false;
    let passValidFlag = false;

    // Username validation rules
    if (username === "") {
      setUserValidation({ status: 'idle', message: '' });
    } else if (username.length < 5) {
      setUserValidation({ status: 'error', message: t.userShort });
    } else if (emailRegex.test(username) || usernameRegex.test(username)) {
      setUserValidation({ status: 'success', message: t.userSuccess });
      userValidFlag = true;
    } else {
      setUserValidation({ status: 'error', message: t.userShort });
    }
    setIsUserValid(userValidFlag);

    // Password validation rules
    if (password === "") {
      setPassValidation({ status: 'idle', message: '' });
    } else if (password.length < 4) {
      setPassValidation({ status: 'error', message: t.passShort });
    } else if (!(hasUpper.test(password) && hasLower.test(password) && hasDigit.test(password) && hasSpecial.test(password))) {
      setPassValidation({ status: 'error', message: t.passWeak });
    } else {
      setPassValidation({ status: 'success', message: t.passSuccess });
      passValidFlag = true;
    }
    setIsPassValid(passValidFlag);

  }, [username, password, currentLang, isLockedOut, t]);

  return {
    userValidation,
    passValidation,
    isUserValid,
    isPassValid,
  };
};