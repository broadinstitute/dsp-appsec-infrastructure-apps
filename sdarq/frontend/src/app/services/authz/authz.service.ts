import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class AuthzService {

  private URL = location.origin + '/user-details/';

  constructor(private http: HttpClient) {}

  fetchUserDetails(): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.get(this.URL,options).pipe(
      catchError(this.handleError)
    );
  }

handleError(error) {

  let errorMessage = '';

  if (error.error instanceof ErrorEvent) {
    // client-side error
    errorMessage = `${error.error.message}`;
  } else {
    // server-side error
    if (error.error.statusText) {
      errorMessage = `${error.error.statusText}`;
    } else {
      errorMessage = `${error.message}`;
    }
  }
  return throwError(errorMessage);
}
}