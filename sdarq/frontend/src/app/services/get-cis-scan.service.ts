import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class GetCisScanService {

  private Url = location.origin + '/cis_results/';

  constructor(private http: HttpClient) { }

  getCisScan(data: string): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.post(this.Url, data, options).pipe(map(res => res)
    )
  }
}
