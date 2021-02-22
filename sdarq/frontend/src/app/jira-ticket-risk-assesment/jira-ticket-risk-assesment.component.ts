import { Component, OnInit } from '@angular/core';
import formJson from './form.json';


@Component({
  selector: 'app-jira-ticket-risk-assesment',
  templateUrl: './jira-ticket-risk-assesment.component.html',
  styleUrls: ['./jira-ticket-risk-assesment.component.css']
})
export class JiraTicketRiskAssesmentComponent implements OnInit {

  constructor() { }

  ngOnInit(): void { }

  json = formJson

  sendData(result) { }
}
