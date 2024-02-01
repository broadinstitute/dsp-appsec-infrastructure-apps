import { Injectable } from '@angular/core';
import { HttpHeaders,HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthzService {

  private URL = location.origin + '/api/user-details/';
  private userGroups: string[] = [];
  private userDetails: any;

  constructor(private http: HttpClient) {}

  fetchUserDetails(): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    console.log(this.http.get(this.URL,options))
    return this.http.get(this.URL,options);
  }

  setUserGroups(groups: string[]): void {
    this.userGroups = groups;
  }

  setUserDetails(details: any): void {
    this.userDetails = details;
  }

  getUserDetails(): any {
    console.log(this.userDetails)
    return this.userDetails;
  }

  isAuthorized(): boolean {
    // include full group name
    const isInGroup = this.userGroups.includes('appsec@broadinstitute.org');

    return isInGroup;
}
}