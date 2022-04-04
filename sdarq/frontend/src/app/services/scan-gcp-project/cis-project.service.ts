import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CisProjectService {

  private Url = location.origin + '/cis_scan/';

  constructor(private http: HttpClient) { }

  sendCisProject(data): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json', 'Accept': 'application/json' }),
    };
    return this.http.post(this.Url, data, options).pipe(
      catchError(this.handleError)
    )
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
