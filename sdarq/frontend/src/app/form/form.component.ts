import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../send-form-data.service';
import { HttpClient } from '@angular/common/http';
import  formJson from './form.json';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css']
})
export class FormComponent implements OnInit {
  constructor(private sendForm: SendFormDataService, private http: HttpClient) { }

  ngOnInit() {}

  json = formJson

  sendData(result) {
      this.sendForm.sendFormData(result).subscribe((res) => {
          console.log('Form sent');
        },
        (res) => {
        });
    }
}
