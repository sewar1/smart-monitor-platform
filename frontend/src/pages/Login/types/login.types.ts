// =========================================================================
// LOGIN TYPES & INTERFACES DEFINITIONS
// =========================================================================

export type LanguageCode = 'en' | 'de';

export interface TranslationSet {
  titleMain: string;
  titleSub: string;
  lblUsername: string;
  lblPassword: string;
  lnkForgot: string;
  btnSubmit: string;
  modalTitle: string;
  modalDesc: string;
  modalClose: string;
  langBtn: string;
  userShort: string;
  userSuccess: string;
  passShort: string;
  passWeak: string;
  passSuccess: string;
}

export type ValidationStatus = 'idle' | 'success' | 'error';

export interface ValidationState {
  status: ValidationStatus;
  message: string;
}