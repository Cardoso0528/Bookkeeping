import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  GoogleOAuthRequest,
  RefreshTokenRequest,
  AuthError,
} from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080/api';

async function authCall<T>(
  endpoint: string,
  body: unknown,
  expectJson = true
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/auth${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    let errorData: AuthError;
    try {
      const json = await response.json();
      errorData = {
        message: json.message || json.error || 'Authentication failed',
        status: response.status,
        errors: json.errors,
      };
    } catch {
      errorData = {
        message: response.status === 429
          ? 'Too many attempts. Please try again later.'
          : 'Authentication failed. Please try again.',
        status: response.status,
      };
    }
    throw errorData;
  }

  if (!expectJson) return undefined as T;
  return response.json();
}

export const authApi = {
  register: (data: RegisterRequest) =>
    authCall<AuthResponse>('/register', data),

  login: (data: LoginRequest) =>
    authCall<AuthResponse>('/login', data),

  googleOAuth: (data: GoogleOAuthRequest) =>
    authCall<AuthResponse>('/oauth2/google', data),

  refresh: (data: RefreshTokenRequest) =>
    authCall<AuthResponse>('/refresh', data),

  logout: (data: RefreshTokenRequest) =>
    authCall<void>('/logout', data, false),
};

// Token storage utilities
const ACCESS_TOKEN_KEY = 'bk_access_token';
const REFRESH_TOKEN_KEY = 'bk_refresh_token';
const USER_KEY = 'bk_user';

export const tokenStorage = {
  getAccessToken: (): string | null =>
    localStorage.getItem(ACCESS_TOKEN_KEY),

  getRefreshToken: (): string | null =>
    localStorage.getItem(REFRESH_TOKEN_KEY),

  getUser: () => {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  setTokens: (auth: AuthResponse) => {
    localStorage.setItem(ACCESS_TOKEN_KEY, auth.accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, auth.refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(auth.user));
  },

  clear: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },
};
