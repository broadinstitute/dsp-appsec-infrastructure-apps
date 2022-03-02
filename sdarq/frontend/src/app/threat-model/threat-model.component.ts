import { Component, OnInit } from '@angular/core';
import { RequestTmService } from '../services/threat-model-request/request-tm.service';
import { HttpClient } from '@angular/common/http';
import formJson from './form.json';

@Component({
  selector: 'app-threat-model',
  templateUrl: './threat-model.component.html',
  styleUrls: ['./threat-model.component.css']
})
export class ThreatModelComponent implements OnInit {

  showForm: boolean;
  showModalError: boolean;

  constructor(private sendForm: RequestTmService, private http: HttpClient) { }

  ngOnInit(): void {
    this.showForm = true;
    this.showModalError = false;
  }

  json = formJson

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe((res) => {
      this.showForm = true;
      this.showModalError = false;
    },
      (res) => { 
        this.showForm = false;
        this.showModalError = true;
      });
  }
}
