import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { JiraTicketRiskAssessmentService } from '../services/jira-ticket-risk-assessment/jira-ticket-risk-assessment.service';


@Component({
  selector: 'app-jira-ticket-risk-assesment',
  templateUrl: './jira-ticket-risk-assesment.component.html',
  styleUrls: ['./jira-ticket-risk-assesment.component.css']
})
export class JiraTicketRiskAssesmentComponent implements OnInit {

  constructor(private sendJTRAForm: JiraTicketRiskAssessmentService) { }

  ngOnInit(): void { }

  json = formJson

  sendData(result) {
    this.sendJTRAForm.sendJTRAFormData(result).subscribe((data) => {})
}
}
