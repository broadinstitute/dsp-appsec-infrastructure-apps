import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../services/send-form-data.service';
import { CisProjectService } from '../services/cis-project.service';
import formJson from './form.json';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {
  constructor(private sendForm: SendFormDataService, private scanGCPproject: CisProjectService) { }

  ngOnInit() { }

  json = formJson

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe((res) => {
    },
      (res) => { });
    if (result.project_id) {
      this.scanGCPproject.sendCisProject(result.project_id).subscribe((res1) => {
      },
        (res1) => { });
    }
  }
}
