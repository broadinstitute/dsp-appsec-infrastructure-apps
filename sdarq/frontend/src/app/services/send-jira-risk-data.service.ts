import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpHeaders, HttpClient } from '@angular/common/http';


@Injectable({
  providedIn: 'root'
})
export class SendJiraRiskDataService {

  private Url = location.origin + '/jira_ticket_risk_assesment/';

  constructor(private http: HttpClient) { }

  sendJiraData(data): Observable<any> {
    const options = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' }),
    };
    return this.http.post(this.Url, data, options);
  }
}
