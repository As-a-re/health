// API client for the health assistant
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

interface HealthQueryRequest {
  question: string;
  language?: string;
  include_translation?: boolean;
}

interface HealthQueryResponse {
  response: string;
  confidence: number;
  language: string;
  model_used: string;
  query_id?: string;
  translation?: Record<string, string>;
}

interface UserCredentials {
  email: string;
  password: string;
}

interface UserRegistration extends UserCredentials {
  full_name?: string;
  preferred_language?: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    full_name?: string;
    preferred_language: string;
    is_active: boolean;
    created_at: string;
  };
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;

    // Load token from localStorage if available
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const url = `${this.baseUrl}${endpoint}`;
      
      // Create headers object
      const headers = new Headers();
      
      // Add default content type if not already set
      const contentTypeHeader = options.headers && (
        (options.headers as Headers).get?.('Content-Type') ||
        (options.headers as Record<string, string>)?.['Content-Type'] ||
        (options.headers as Record<string, string>)?.['content-type']
      );
      
      if (!contentTypeHeader && !(options.body instanceof FormData)) {
        headers.append('Content-Type', 'application/json');
      }
      
      // Add any custom headers
      if (options.headers) {
        if (options.headers instanceof Headers) {
          options.headers.forEach((value, key) => {
            headers.set(key, value);
          });
        } else if (Array.isArray(options.headers)) {
          options.headers.forEach(([key, value]) => {
            headers.set(key, value);
          });
        } else {
          Object.entries(options.headers).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              value.forEach((v: string) => headers.append(key, v));
            } else if (value) {
              headers.set(key, value as string);
            }
          });
        }
      }
      
      // Add auth header if token exists
      if (this.token) {
        headers.set('Authorization', `Bearer ${this.token}`);
      }

      const fetchOptions: RequestInit = {
        ...options,
        headers,
      };

      const response = await fetch(url, fetchOptions);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || `HTTP ${response.status}`;
        throw new Error(errorMessage);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      console.error("API request failed:", error);
      return { 
        error: error instanceof Error ? error.message : "Unknown error" 
      };
    }
  }

  // Authentication methods
  async register(userData: UserRegistration): Promise<ApiResponse<AuthResponse>> {
    const response = await this.request<AuthResponse>("/auth/register", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (response.data) {
      this.setToken(response.data.access_token);
    }

    return response;
  }

  async login(credentials: UserCredentials): Promise<ApiResponse<AuthResponse>> {
    // Convert credentials to URL-encoded form data
    const formData = new URLSearchParams();
    formData.append('email', credentials.email);
    formData.append('password', credentials.password);

    const response = await this.request<AuthResponse>("/auth/login", {
      method: "POST",
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
      },
      body: formData.toString(),
    });

    if (response.data) {
      this.setToken(response.data.access_token);
    }

    return response;
  }

  async getCurrentUser(): Promise<ApiResponse<AuthResponse['user']>> {
    return this.request<AuthResponse['user']>("/auth/me");
  }

  logout(): void {
    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
    }
  }

  private setToken(token: string): void {
    this.token = token;
    if (typeof window !== "undefined") {
      localStorage.setItem("auth_token", token);
    }
  }

  // Health query methods
  async askHealthQuestion(
    query: HealthQueryRequest
  ): Promise<ApiResponse<HealthQueryResponse>> {
    try {
      const response = await this.request<HealthQueryResponse>("/health/ask", {
        method: "POST",
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query.question,
          language: query.language || 'auto',
          include_translation: query.include_translation || false
        }),
      });

      // Handle specific error cases
      if (response.error) {
        console.error('[Health API] Error:', response.error);
        if (response.error.includes('401')) {
          this.logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
      }
      
      return response;
    } catch (error) {
      console.error('[Health API] Request failed:', error);
      return {
        error: error instanceof Error ? error.message : 'Failed to process health question'
      };
    }
  }

  async askHealthQuestionAudio(
    audioFile: File, 
    language = "auto"
  ): Promise<ApiResponse<unknown>> {
    const formData = new FormData();
    formData.append("audio_file", audioFile);
    formData.append("language", language);

    try {
      const response = await this.request("/api/health/ask-audio", {
        method: "POST",
        body: formData,
        // Don't set Content-Type header, let the browser set it with the correct boundary
        headers: {
          'Accept': 'application/json',
        },
      });

      return response;
    } catch (error) {
      console.error("Audio API request failed:", error);
      return {
        error: error instanceof Error ? error.message : "Failed to process audio question"
      };
    }
  }

  // User profile methods
  async getUserHistory(
    page = 1, 
    pageSize = 20
  ): Promise<ApiResponse<unknown>> {
    return this.request("/user/history", {
      method: "GET",
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async updateUserProfile(
    profileData: Record<string, unknown>
  ): Promise<ApiResponse<unknown>> {
    return this.request("/user/profile", {
      method: "PUT",
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string }>> {
    return this.request<{ status: string }>("/api/health");
  }
}

// Create singleton instance
export const api = new ApiClient();
