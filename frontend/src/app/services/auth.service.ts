import { inject, Injectable } from '@angular/core';
import { catchError, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';

interface AuthRequest {
  email: string;
  password: string; // Assuming there's also a password field
}

interface TokenResponse {
  token: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = `${environment.apiBaseUrl}`;
  private http = inject(HttpClient);

  private currentUserType: string = ""

  constructor() { }

    checkGroup(id: string): Observable<any> {
      return this.http.get(`${this.apiUrl}/auth/check-group${id}`);
    }

    loginUser(email: string, userType: string): Observable<TokenResponse> {

      const authRequest = { email: email, userType: userType };
      
      const headers = new HttpHeaders({
        'Content-Type': 'application/json'
      });
    
      return this.http.post<TokenResponse>(
        `${this.apiUrl}/auth/login`,
        authRequest,
        { headers }
      ).pipe(
        tap(response => {
          // Store the token in localStorage or a service
          if (response.token) {
            localStorage.setItem('current_logged_in_user', email);
            localStorage.setItem('auth_token', response.token);
          }
        })
      );
    }
  

    getGroups(): Observable<any> {
      const headers = new HttpHeaders({
        'Authorization': 'Bearer ' + this.getToken()
      });
      
      return this.http.get(`${this.apiUrl}/auth/groups`, { headers });
    }

      // You might also want to add a method to get the current token
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  getCurrentUser(): string | null {
    return localStorage.getItem('current_logged_in_user');
  }

  // And a method to logout/remove the token
  logout(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('current_logged_in_user');
  }

  setCurrentUserType(type: string): void {
    this.currentUserType = type;
  }

  getCurrentUserType(): string {
    return this.currentUserType;
  }
  
}
