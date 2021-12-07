import { Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { catchError, map } from 'rxjs/operators';
import { ServiceSecurityControl } from '../../models/service-security-control.model';


@Injectable({
  providedIn: 'root'
})
export class GetSecurityControlsService {

  private URL = location.origin + '/get_sec_controls/';


  constructor(private http: HttpClient) { }

  getAllSecurityControls(): Observable<ServiceSecurityControl[]> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.get<ServiceSecurityControl[]>(this.URL, options).pipe(
      map(res => res.map((serviceSecurityControl: ServiceSecurityControl) => new ServiceSecurityControl().deserialize(serviceSecurityControl))), // tslint:disable-line
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
