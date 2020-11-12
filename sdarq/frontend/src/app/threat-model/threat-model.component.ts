import { Component, OnInit } from '@angular/core';
import { RequestTmService } from '../services/request-tm.service';
import { HttpClient } from '@angular/common/http';
import formJson from './form.json';

@Component({
  selector: 'app-threat-model',
  templateUrl: './threat-model.component.html',
  styleUrls: ['./threat-model.component.css']
})
export class ThreatModelComponent implements OnInit {

  constructor(private sendForm: RequestTmService, private http: HttpClient) { }

  ngOnInit(): void {
  }

  json = formJson

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe((res) => {
      console.log('Form sent');
    },
      (res) => { });
  }
}
