import { Injectable,signal } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  loggedIn = signal(false);

  constructor(private router: Router) {
    this.loggedIn.set(this.getToken() != '');
  }
  getToken(): string {
    try {
      return localStorage.getItem('token') || '';
    } catch {
      return '';
    }
  }

  saveToken(token: string) {
    try {
      localStorage.setItem('token', token);
    } catch { }
    this.loggedIn.set(true);
  }

  clearToken() {
    try {
      localStorage.removeItem('token');
    } catch { }
    this.loggedIn.set(false);
  }

  // 401 means the token is missing, wrong or finished, so go back to the login page
  handleAuthError(err: any) {
    if (err.status == 401) {
      this.clearToken();
      this.router.navigate(['/login']);
    }
  }
  
}
