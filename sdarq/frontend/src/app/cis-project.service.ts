import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { projectFindings } from './_models/projectFindings';

import {  throwError } from 'rxjs';
import { retry, catchError, map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class CisProjectService {

  private Url = location.origin + '/cis_results/';

  constructor(private http: HttpClient) { }


  sendCisProject(data): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.post(this.Url, data, options).pipe(map(res => res)
          )}
    
}
