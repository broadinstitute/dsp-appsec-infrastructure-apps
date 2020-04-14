import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient, HttpErrorResponse } from '@angular/common/http';
import {  throwError } from 'rxjs';
import { retry, catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CisProjectService {

  // private Url = location.origin + '/cis_results/';
  private Url = 'http://0.0.0.0:8080/cis_results/';

  constructor(private http: HttpClient) { }

  sendCisProject(data): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.post(this.Url, data, options).pipe(map(res => res),
    catchError(this.handleError))}
    
  handleError(error: HttpErrorResponse) {
    let errorMessage = 'ERROR';
    if (error.error instanceof ErrorEvent) {
      // client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // server-side error
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    console.log(errorMessage);
    return throwError(errorMessage);
  }
  }
  