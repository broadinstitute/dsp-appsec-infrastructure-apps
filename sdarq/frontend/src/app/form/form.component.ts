import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../services/send-form-data.service';
import { CisProjectService } from '../services/cis-project.service';
import { CreateNewSctService } from '../services/create-new-sct.service';
import formJson from './form.json';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {

  errors: any;
  json = formJson
  arrRequired = {};
  showAlert: boolean;
  showForm: boolean;

  constructor(private sendForm: SendFormDataService, private scanGCPproject: CisProjectService, private createNewSctService: CreateNewSctService) { }

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

    this.arrRequired = {'service' : result['Service'], 'github': result['Github URL']};
    this.createNewSctService.createNewSCT(this.arrRequired).subscribe((createNewSCTResponse) => {
    });

    if (result.project_id) {
      this.scanGCPproject.sendCisProject(result).subscribe((scanGCPProjectResponse) => {
      });
    }
  }
}
