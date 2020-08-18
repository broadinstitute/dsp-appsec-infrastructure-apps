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

  risk: any;
  data: any[];
  showSpinner: boolean;
  showModal_low: boolean;
  showModal_medium: boolean;
  showModal_high: boolean;
  showForm: boolean;

  constructor(private sendJiraForm: SendJiraRiskDataService, private http: HttpClient) { }

  ngOnInit(): void {
    this.showModal_low = false;
    this.showModal_medium = false;
    this.showModal_high = false;
    this.showForm = true;
  }

  json = formJson

  sendData(result) {
    this.sendJiraForm.sendJiraData(result).subscribe((data: any) => {
      this.risk = data;
      this.showForm = false;
      this.showSpinner = false;
      if (this.risk.Risk == 'Low') {
        this.showModal_low = true;
      }
      else if (this.risk.Risk == 'Medium') {
        this.showModal_medium = true;
      }
      else {
        this.showModal_high = true
      }
    },
      (data) => {
        this.showModal_low = false;
        this.showModal_medium = false;
        this.showModal_high = false;
        this.showForm = false;
        this.showSpinner = true;
      });
  }
}
