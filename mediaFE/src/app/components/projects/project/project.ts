import { Component } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth-service';
import { WebServices } from '../../../web-services/web-services';

@Component({
  selector: 'app-project',
  imports: [RouterModule],
  templateUrl: './project.html',
  styleUrl: './project.css',
})
export class Project {

  project: any = {};
  asset_list: any = [];
  page: number = 1;
  isLastPage: boolean = false;

  constructor(private route: ActivatedRoute,
              private webService: WebServices,
              private auth: AuthService) { }

  ngOnInit() {
    let id = this.route.snapshot.paramMap.get('id');
    this.webService.getProject(id).subscribe({
      next: (response) => this.project = response,
      error: (err) => this.auth.handleAuthError(err)
    });
    this.loadAssets();
  }

  loadAssets() {
    let id = this.route.snapshot.paramMap.get('id');
    this.webService.getAssets(id, this.page).subscribe({
      next: (response) => {
        this.asset_list = response;
        this.isLastPage = response.length < this.webService.pageSize;
      },
      error: (err) => this.auth.handleAuthError(err)
    });
  }

  nextPage() {
    this.page = this.page + 1;
    this.loadAssets();
  }

  previousPage() {
    if (this.page > 1) {
      this.page = this.page - 1;
      this.loadAssets();
    }
  }
}