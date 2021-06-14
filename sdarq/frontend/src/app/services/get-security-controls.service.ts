import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable({
  providedIn: 'root'
})
export class GetSecurityControlsService {

  private Url = location.origin + '/get_sec_controls/';

  constructor(private http: HttpClient) { }

  getAllSecurityControls(): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.get(this.Url, options).pipe(
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
