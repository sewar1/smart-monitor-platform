import { useState } from 'react';
import type { LanguageCode } from '../types/login.types';

export const useLanguage = (initialLang: LanguageCode = 'en') => {
  const [currentLang, setCurrentLang] = useState<LanguageCode>(initialLang);

  const toggleLanguage = () => {
    setCurrentLang((prev) => (prev === 'en' ? 'de' : 'en'));
  };

  return {
    currentLang,
    toggleLanguage,
  };
};