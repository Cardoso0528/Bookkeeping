import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
  type ReactNode,
} from 'react';
import { authApi, tokenStorage } from '../services/auth';
import type {
  UserResponse,
  LoginRequest,
  RegisterRequest,
  AuthError,
} from '../types/auth';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (data: LoginRequest) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return ctx;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const scheduleRefresh = useCallback((expiresIn: number) => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
    // Refresh 60 seconds before expiry (or halfway if token is short-lived)
    const delay = Math.max((expiresIn - 60000), expiresIn / 2);
    refreshTimerRef.current = setTimeout(async () => {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) return;
      try {
        const auth = await authApi.refresh({ refreshToken });
        tokenStorage.setTokens(auth);
        setUser(auth.user);
        scheduleRefresh(auth.expiresIn);
      } catch {
        // Refresh failed — force logout
        tokenStorage.clear();
        setUser(null);
      }
    }, delay);
  }, []);

  // Initialize auth state from storage
  useEffect(() => {
    const storedUser = tokenStorage.getUser();
    const accessToken = tokenStorage.getAccessToken();
    const refreshToken = tokenStorage.getRefreshToken();

    if (storedUser && accessToken) {
      setUser(storedUser);
      // Try to refresh immediately to validate the session
      if (refreshToken) {
        authApi
          .refresh({ refreshToken })
          .then((auth) => {
            tokenStorage.setTokens(auth);
            setUser(auth.user);
            scheduleRefresh(auth.expiresIn);
          })
          .catch(() => {
            tokenStorage.clear();
            setUser(null);
          })
          .finally(() => setIsLoading(false));
      } else {
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }

    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [scheduleRefresh]);

  const login = useCallback(
    async (data: LoginRequest) => {
      const auth = await authApi.login(data);
      tokenStorage.setTokens(auth);
      setUser(auth.user);
      scheduleRefresh(auth.expiresIn);
    },
    [scheduleRefresh]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      const auth = await authApi.register(data);
      tokenStorage.setTokens(auth);
      setUser(auth.user);
      scheduleRefresh(auth.expiresIn);
    },
    [scheduleRefresh]
  );

  const loginWithGoogle = useCallback(
    async (idToken: string) => {
      const auth = await authApi.googleOAuth({ idToken });
      tokenStorage.setTokens(auth);
      setUser(auth.user);
      scheduleRefresh(auth.expiresIn);
    },
    [scheduleRefresh]
  );

  const logout = useCallback(async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (refreshToken) {
      try {
        await authApi.logout({ refreshToken });
      } catch {
        // Ignore logout errors — clear local state anyway
      }
    }
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
    tokenStorage.clear();
    setUser(null);
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    loginWithGoogle,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export type { AuthError };
