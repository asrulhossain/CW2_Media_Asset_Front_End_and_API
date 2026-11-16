import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { WebServices } from '../../web-services/web-services';

@Component({
  selector: 'app-navigation',
  imports: [RouterModule],
  templateUrl: './navigation.html',
  styleUrl: './navigation.css',
})
export class Navigation {

  constructor(public auth: AuthService,
              private webService: WebServices,
              private router: Router) { }
  logout() {
    this.webService.logout().subscribe({
      next: () => this.finishLogout(),
      error: () => this.finishLogout()
    });
  }

  finishLogout() {
    this.auth.clearToken();
    this.router.navigate(['/login']);
  }

}