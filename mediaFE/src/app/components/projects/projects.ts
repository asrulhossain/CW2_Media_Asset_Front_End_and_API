import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { WebServices } from '../../web-services/web-services';

@Component({
  selector: 'app-projects',
  imports: [RouterModule],
  templateUrl: './projects.html',
  styleUrl: './projects.css',
})
export class Projects {

  project_list: any = [];
  page: number = 1;
  isLastPage: boolean = false;

  constructor(private webService: WebServices,
              private auth: AuthService) { }

  ngOnInit() {
    this.loadPage();
  }

  loadPage() {
    this.webService.getProjects(this.page).subscribe({
      next: (response) => {
        this.project_list = response;
        this.isLastPage = response.length < this.webService.pageSize;
      },
      error: (err) => this.auth.handleAuthError(err)
    });
  }

  nextPage() {
    this.page = this.page + 1;
    this.loadPage();
  }

  previousPage() {
    if (this.page > 1) {
      this.page = this.page - 1;
      this.loadPage();
    }
  }
}
