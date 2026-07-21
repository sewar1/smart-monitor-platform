import React, { useState } from 'react';
import { useLanguage } from './hooks/useLanguage';
import { useLoginValidation } from './hooks/useLoginValidation';
import { useLoginEffects } from './hooks/useLoginEffects';
import { translations } from './constants/translations';
import { LoginLayout } from './components/LoginLayout';
import { LoginCard } from './components/LoginCard';
import { LoginHeader } from './components/LoginHeader';
import { LangSwitcher } from './components/LangSwitcher';
import { LoginForm } from './components/LoginForm';
import { LoginFooter } from './components/LoginFooter';
import { RecoveryModal } from './components/RecoveryModal';

export const Login: React.FC = () => {
  const { currentLang, toggleLanguage } = useLanguage('en');
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLockedOut] = useState<boolean>(false);
  const [globalError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  const t = translations[currentLang];

  const { userValidation, passValidation, isUserValid, isPassValid } = useLoginValidation(
    username,
    password,
    currentLang,
    isLockedOut
  );

  const { glowColor } = useLoginEffects(
    username,
    password,
    isUserValid,
    isPassValid,
    isLockedOut
  );

  const isFormValid = isUserValid && isPassValid && !isLockedOut;

  const handleLoginSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    localStorage.setItem('monitor_jwt_token', 'mock_token_for_testing');
    setTimeout(() => {
      window.location.href = '/dashboard';
    }, 600);
  };

  return (
    <LoginLayout>
      <LoginCard glowColor={glowColor} shouldShake={false}>
        <div>
          <div className="flex justify-end mb-6">
            <LangSwitcher currentLang={currentLang} onToggle={toggleLanguage} />
          </div>
          <LoginHeader titleMain={t.titleMain} titleSub={t.titleSub} />
        </div>

        <div className="my-auto">
          {globalError && (
            <div id="global-alert" className="mb-6 p-3.5 rounded-xl text-start text-xs bg-red-500/15 border border-red-500/30 text-red-400 font-medium shadow-md">
              {globalError}
            </div>
          )}

          <LoginForm
            username={username}
            onUsernameChange={(e) => setUsername(e.target.value)}
            userValidation={userValidation}
            password={password}
            onPasswordChange={(e) => setPassword(e.target.value)}
            passValidation={passValidation}
            showPassword={showPassword}
            onToggleShowPassword={() => setShowPassword(!showPassword)}
            isLockedOut={isLockedOut}
            isLoading={isLoading}
            isFormValid={isFormValid}
            currentLang={currentLang}
            submitButtonText={t.btnSubmit}
            onSubmit={handleLoginSubmit}
          />
        </div>

        <LoginFooter lnkForgot={t.lnkForgot} onOpenModal={() => setIsModalOpen(true)} />
      </LoginCard>

      <RecoveryModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        translations={{
          modalTitle: t.modalTitle,
          modalDesc: t.modalDesc,
          modalClose: t.modalClose,
        }}
      />
    </LoginLayout>
  );
};