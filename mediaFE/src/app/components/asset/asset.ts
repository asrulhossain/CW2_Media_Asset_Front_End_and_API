import { Component } from '@angular/core';
import { ActivatedRoute, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { WebServices } from '../../web-services/web-services';

@Component({
  selector: 'app-asset',
  imports: [RouterModule],
  templateUrl: './asset.html',
  styleUrl: './asset.css',
})
export class Asset {

  asset: any = {};

  constructor(private route: ActivatedRoute,
              private webService: WebServices,
              private auth: AuthService) { }

  ngOnInit() {
    let id = this.route.snapshot.paramMap.get('id');
    this.webService.getAsset(id).subscribe({
      next: (response) => this.asset = response,
      error: (err) => this.auth.handleAuthError(err)
    });
  }
}