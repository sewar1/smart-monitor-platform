import { useState, useEffect } from 'react';

export const useLoginEffects = (username: string, password: string, isUserValid: boolean, isPassValid: boolean, isLockedOut: boolean) => {
  const [glowColor, setGlowColor] = useState<string>('rgba(59, 130, 246, 0.15)');

  useEffect(() => {
    if (isLockedOut) return;

    if (username !== "" || password !== "") {
      if (isUserValid && isPassValid) {
        setGlowColor('rgba(16, 185, 129, 0.35)'); // Green glow on full success
      } else if ((!isUserValid && username.length >= 5) || (!isPassValid && password.length >= 4)) {
        setGlowColor('rgba(239, 68, 68, 0.35)'); // Red glow on error criteria
      } else {
        setGlowColor('rgba(59, 130, 246, 0.35)'); // Blue glow on active typing
      }
    } else {
      setGlowColor('rgba(59, 130, 246, 0.15)'); // Default idle glow
    }
  }, [username, password, isUserValid, isPassValid, isLockedOut]);

  return {
    glowColor,
  };
};