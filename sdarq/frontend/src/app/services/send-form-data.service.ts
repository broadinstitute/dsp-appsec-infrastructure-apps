import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})

export class SendFormDataService {

  // private Url = location.origin + '/submit/';

  private Url='http://0.0.0.0:8080/submit/'
  
  constructor(private http: HttpClient) { }

  sendFormData(data): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.post(this.Url, data, options) ;
  }
}
