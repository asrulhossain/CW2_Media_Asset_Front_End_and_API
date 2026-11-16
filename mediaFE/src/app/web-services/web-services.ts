import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from '../services/auth-service';

@Injectable({
  providedIn: 'root',
})
export class WebServices {
  pageSize: number = 3;
  baseUrl: string = 'http://127.0.0.1:5001/api/v1.0';

  constructor(private http: HttpClient,
              private auth: AuthService) { }

  private tokenHeader() {
    return { headers: new HttpHeaders({ 'x-access-token': this.auth.getToken() }) };
  }
  login(email: string, password: string) {
    return this.http.post<any>(this.baseUrl + '/login', {},
      { headers: new HttpHeaders({ 'Authorization': 'Basic ' + btoa(email + ':' + password) }) });
  }
  logout() {
    return this.http.get<any>(this.baseUrl + '/logout', this.tokenHeader());
  }

    getProjects(page: number) {
    return this.http.get<any[]>(
      this.baseUrl + '/projects?pn=' + page + '&ps=' + this.pageSize, this.tokenHeader());
  }

  getProject(id: any) {
    return this.http.get<any>(this.baseUrl + '/projects/' + id, this.tokenHeader());
  }

  getAssets(projectId: any, page: number) {
    return this.http.get<any[]>(
      this.baseUrl + '/projects/' + projectId + '/assets?pn=' + page + '&ps=' + this.pageSize,
      this.tokenHeader());
  }

    getAsset(id: any) {
    return this.http.get<any>(this.baseUrl + '/assets/' + id, this.tokenHeader());
  }

}              
