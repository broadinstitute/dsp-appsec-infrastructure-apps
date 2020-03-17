import { Injectable } from '@angular/core';
import {Observable} from 'rxjs';
import { map } from 'rxjs/operators';
import { Http , Response , RequestOptions, Headers } from '@angular/http' ;
import {HttpHeaders, HttpClient} from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})

export class SendFormDataService {

  private Url = location.origin + '/submit/';
  constructor(private http: Http) { }
 
  sendFormData(data): Observable<any> {
    const headers = new Headers({ 'Content-Type': 'application/json' }) ;
    const options = new RequestOptions({ headers}) ;
    return this.http.post(this.Url, data, options) ;
  }

  private extractData(res: Response) {  
    const body = res.json();
    return body;
  }

}
