import { Injectable } from '@angular/core';
import { HttpHeaders ,HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, tap } from 'rxjs/operators';


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
    return this.http.get(this.URL,options).pipe(
      catchError(this.handleError),
      tap(response => {
        if (response && response.groups) {
          this.setUserGroups(response.groups);
          console.log(this.setUserGroups(response.groups))
        }
      })
    );
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
    const isInGroup = this.userGroups.includes('appsec@broadinstitute.org');
    console.log(isInGroup)
    return isInGroup;
}

handleError(error) {

  let errorMessage = '';

  if (error.error instanceof ErrorEvent) {
    // client-side error
    console.log(errorMessage)
    errorMessage = `${error.error.message}`;
  } else {
    // server-side error
    if (error.error.statusText) {
      console.log(errorMessage)
      errorMessage = `${error.error.statusText}`;
    } else {
      console.log(errorMessage)
      errorMessage = `${error.message}`;
    }
  }
  return throwError(errorMessage);
}
}