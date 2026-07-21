// =========================================================================
// REGEX VALIDATION UTILITIES
// =========================================================================

export const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
export const usernameRegex = /^[a-zA-Z0-9_.-]{3,50}$/;
export const hasUpper = /[A-Z]/;
export const hasLower = /[a-z]/;
export const hasDigit = /[0-9]/;
export const hasSpecial = /[^A-Za-z0-9]/;