import { Component, OnInit } from '@angular/core';
import { SendJiraRiskDataService } from '../services/send-jira-risk-data.service';
import { HttpClient } from '@angular/common/http';
import formJson from './form.json';


@Component({
  selector: 'app-jira-ticket-risk-assesment',
  templateUrl: './jira-ticket-risk-assesment.component.html',
  styleUrls: ['./jira-ticket-risk-assesment.component.css']
})
export class JiraTicketRiskAssesmentComponent implements OnInit {

  risk: any[];
  data: any[];
  showSpinner: boolean;
  showModal: boolean;
  showForm: boolean;

  constructor(private sendJiraForm: SendJiraRiskDataService, private http: HttpClient) { }

  ngOnInit(): void {
    this.showModal = false;
    this.showForm = true;
    this.showModal = false;
  }

  json = formJson

  sendData(result) {
    this.sendJiraForm.sendJiraData(result).subscribe((data: any) => {
      this.risk = data;
      this.showModal = true;
      this.showForm = false;
      this.showSpinner = false;
    },
      (data) => { });
  }
}
