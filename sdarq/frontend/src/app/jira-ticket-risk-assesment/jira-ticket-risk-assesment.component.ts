import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import formJson from './form.json';
import { JiraTicketRiskAssessmentService } from '../services/jira-ticket-risk-assessment/jira-ticket-risk-assessment.service';


@Component({
  selector: 'app-jira-ticket-risk-assesment',
  templateUrl: './jira-ticket-risk-assesment.component.html',
  styleUrls: ['./jira-ticket-risk-assesment.component.css']
})
export class JiraTicketRiskAssesmentComponent implements OnInit {

  showModalErr: boolean;
  showModal: boolean;
  showForm: boolean;
  showModalError: any;
  showModalMessage: any;

  constructor(private sendJTRAForm: JiraTicketRiskAssessmentService,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) {
                // This is intentional
               }

  ngOnInit(): void {
    this.showModalErr = false;
    this.showForm = true;
    this.showModal = false;
   }

  json = formJson

  sendData(result) {
    this.sendJTRAForm.sendJTRAFormData(result).subscribe((res) => {
      this.ref.detectChanges();
      this.showModal = true;
      console.log(res)
      console.log(res.statusText)
      console.log(res["statusText"])
      this.showModalMessage = res["statusText"];
    },
      (res) => {
        this.ngZone.run(() => {
        this.showModalErr = true;
        this.showForm = false;
        this.showModalError = res;
      });
    });
  }
}