import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { WebServices } from '../../web-services/web-services';

@Component({
  selector: 'app-login',
  imports: [FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {

  email: string = '';
  password: string = '';
  message: string = '';

  constructor(private webService: WebServices,
              private auth: AuthService,
              private router: Router) { }

  login() {
    this.message = '';
    this.webService.login(this.email, this.password).subscribe({
      next: (response) => {
        this.auth.saveToken(response.token);
        this.router.navigate(['/']);
      },
      error: (err) => {
        if (err.status == 401) {
          this.message = 'Wrong email or password';
        } else if (err.status == 0) {
          this.message = 'Cannot reach the API. Is Flask running on port 5001 and is flask-cors installed?';
        } else {
          this.message = 'Login failed, status ' + err.status;
        }
      }
    });
  }
}