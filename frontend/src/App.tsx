
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import React from 'react';
import { Dashboard } from './pages/Dashboard/Dashboard';
import { Login } from './pages/Login/Login';

// دالة بسيطة للتحقق من تسجيل الدخول عبر الـ Token
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = localStorage.getItem('monitor_jwt_token');
  // إذا لم يكن هناك توكن، قم بتحويله إلى صفحة تسجيل الدخول فوراً
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} /> 
        <Route 
          path="/" 
          element={
            localStorage.getItem('monitor_jwt_token') 
              ? <Navigate to="/dashboard" replace /> 
              : <Navigate to="/login" replace />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;