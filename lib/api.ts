// API client for the health assistant
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status?: number;
}

interface UserCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    full_name: string;
    preferred_language: string;
    is_active: boolean;
    created_at?: string;
  };
  expires_in?: number;
}

interface HealthQueryRequest {
  question: string;
  language?: string;
  include_translation?: boolean;
}

interface HealthQueryResponse {
  response: string;
  language: string;
  confidence?: number;
  model_used?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
    this.loadToken();
  }

  private loadToken(): void {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  public setToken(token: string | null): void {
    this.token = token;
    if (typeof window !== "undefined") {
      if (token) {
        localStorage.setItem("auth_token", token);
      } else {
        localStorage.removeItem("auth_token");
      }
    }
  }

  async askHealthQuestion(
    query: HealthQueryRequest
  ): Promise<ApiResponse<HealthQueryResponse>> {
    return this.request<HealthQueryResponse>("/health/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(query),
    });
  }

  async askHealthQuestionAudio(
    audioFile: File,
    language = "auto"
  ): Promise<ApiResponse<HealthQueryResponse>> {
    const formData = new FormData();
    formData.append("audio_file", audioFile);
    formData.append("language", language);

    return this.request<HealthQueryResponse>("/health/speak", {
      method: "POST",
      body: formData,
      // Don't set Content-Type header, let the browser set it with the correct boundary
      headers: {
        'Accept': 'application/json',
      },
    });
  }

  // Authentication methods
  async login(credentials: UserCredentials): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await this.request<AuthResponse>("/auth/login", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email: credentials.email,
          password: credentials.password
        }),
      });
      
      console.log('[API] Login response:', response);
      return response;
    } catch (error) {
      console.error('[API] Login error:', error);
      return { 
        error: error instanceof Error ? error.message : 'Login failed. Please try again.',
        status: 500
      };
    }
  }

  async getCurrentUser(): Promise<ApiResponse<AuthResponse['user']>> {
    try {
      const response = await this.request<{ user: AuthResponse['user'] }>("/auth/me");
      return {
        data: response.data?.user,
        error: response.error,
        status: response.status
      };
    } catch (error) {
      console.error('[API] Get current user error:', error);
      return { 
        error: error instanceof Error ? error.message : 'Failed to fetch current user',
        status: 401
      };
    }
  }

  async register(userData: {
    email: string;
    password: string;
    full_name: string;
    preferred_language?: string;
  }): Promise<ApiResponse<AuthResponse>> {
    try {
      const response = await this.request<AuthResponse>("/auth/signup", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          full_name: userData.full_name,
          preferred_language: userData.preferred_language || 'en'
        }),
      });
      
      console.log('[API] Register response:', response);
      return response;
    } catch (error) {
      console.error('[API] Register error:', error);
      return { 
        error: error instanceof Error ? error.message : 'Registration failed. Please try again.',
        status: 500
      };
    }
  }

  async logout(): Promise<{ success: boolean }> {
    try {
      // Clear the token from the API client and localStorage
      this.setToken(null);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
      }
      return { success: true };
    } catch (error) {
      console.error('[API] Logout error:', error);
      return { success: false };
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const headers = new Headers(options.headers);
    const isJson = headers.get('Content-Type')?.includes('application/json');
    
    // Always get the latest token from localStorage in case it was updated
    const token = this.token || (typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null);
    
    if (token && !endpoint.startsWith('/auth/')) {
      headers.set('Authorization', `Bearer ${token}`);
      console.log('[API] Added Authorization header to request');
    } else {
      console.log('[API] No token available for request');
    }

    try {
      console.log(`[API] ${options.method || 'GET'} ${endpoint}`, {
        headers: Object.fromEntries(headers.entries()),
        body: options.body ? (isJson ? JSON.parse(options.body as string) : options.body) : undefined
      });

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers,
      });

      const responseData = await response.json().catch(() => ({}));
      
      if (!response.ok) {
        console.error(`[API] Request failed: ${response.status}`, {
          status: response.status,
          statusText: response.statusText,
          url: `${this.baseUrl}${endpoint}`,
          response: responseData,
        });
        
        if (response.status === 422 && responseData.detail) {
          // Handle validation errors
          const errorMessage = Array.isArray(responseData.detail) 
            ? responseData.detail.map((d: any) => d.msg || d.message).join('; ')
            : responseData.detail;
          throw new Error(errorMessage || 'Validation failed');
        }
        
        throw new Error(
          responseData.detail || 
          responseData.message || 
          `Request failed with status ${response.status}`
        );
      }

      return { data: responseData };
    } catch (error) {
      console.error(`[API] Request failed:`, error);
      return { 
        error: error instanceof Error 
          ? error.message 
          : typeof error === 'string' 
            ? error 
            : 'An unknown error occurred' 
      };
    }
  }
}

const api = new ApiClient();
const apiClient = api; // For backward compatibility

export { api, apiClient };
