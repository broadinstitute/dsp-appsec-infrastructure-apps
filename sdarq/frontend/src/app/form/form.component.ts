import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../services/create-new-service/send-form-data.service';
import { CisProjectService } from '../services/scan-gcp-project/cis-project.service';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';
import formJson from './form.json';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {

  errors: string;
  json = formJson
  arrRequired = {};
  showAlert: boolean;
  showForm: boolean;

  constructor(private sendForm: SendFormDataService,
              private scanGCPproject: CisProjectService,
              private createNewSctService: CreateNewSctService) { }

  ngOnInit() {
    this.showForm = true;
  }

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe((submitNewServiceQuestionnaireResponse) => {
    },
      (submitNewServiceQuestionnaireResponse) => {
        this.showAlert = true;
        this.showForm = false;
        this.errors = submitNewServiceQuestionnaireResponse;
      });

    this.arrRequired = {
      'service': result['Service'],
      'github': result['Github URL'],
      'security_champion': result['Security champion'],
      'product': result['Product']
    };
    this.createNewSctService.createNewSCT(this.arrRequired).subscribe((createNewSCTResponse) => {
      console.log("Security Controls template created for this service")
    });

    if (result.project_id) {
      this.scanGCPproject.sendCisProject(result).subscribe((scanGCPProjectResponse) => {
        console.log("CIS scanner running against GCP project")
      });
    }
  }
}
