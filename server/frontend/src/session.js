import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from './api';

const SessionContext = createContext();
export const useSession = () => useContext(SessionContext);

export function SessionProvider({ children }) {
  const [session, setSession] = useState({ authenticated: false, loading: true });
  const [sessionError, setSessionError] = useState('');
  async function refreshSession() {
    try {
      const data = await api('session');
      setSession({ ...data, loading: false });
      setSessionError('');
      return data;
    } catch (error) {
      setSession({ authenticated: false, loading: false });
      setSessionError(error.message);
      throw error;
    }
  }
  useEffect(() => { refreshSession().catch(() => {}); }, []);
  return <SessionContext.Provider value={{ ...session, refreshSession }}>
    {sessionError && <p className="notice error" role="alert">Session unavailable: {sessionError}</p>}
    {children}
  </SessionContext.Provider>;
}
