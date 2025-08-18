'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface UserInfo {
  user_id: string;
  location_id: string | null;
  device_serial: string | null;
  full_name: string;
  iat: number;
  exp: number;
  created_at: string;
}

interface AuthContextType {
  userInfo: UserInfo | null;
  loading: boolean;
  setUserInfo: (userInfo: UserInfo | null) => void;
  getUserId: () => string | null;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [userInfo, setUserInfo] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUserInfo = localStorage.getItem('user_info');
    if (storedUserInfo) {
      try {
        const parsedUserInfo = JSON.parse(storedUserInfo);
        setUserInfo(parsedUserInfo);
      } catch (error) {
        console.error('Error parsing stored user info:', error);
        localStorage.removeItem('user_info');
      }
    }
    setLoading(false);
  }, []);

  const getUserId = (): string | null => {
    return userInfo?.user_id || null;
  };

  const logout = () => {
    setUserInfo(null);
    localStorage.removeItem('user_info');
    document.cookie = 'jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  };

  return (
    <AuthContext.Provider value={{
      userInfo,
      loading,
      setUserInfo,
      getUserId,
      logout,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
