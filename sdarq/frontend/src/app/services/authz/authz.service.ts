import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class AuthzService {

  private URL = location.origin + '/api/user-details/';

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