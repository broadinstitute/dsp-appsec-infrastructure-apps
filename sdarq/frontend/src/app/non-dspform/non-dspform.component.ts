import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../services/send-form-data.service';
import formJson from './newForm.json';

@Component({
  selector: 'app-non-dspform',
  templateUrl: './non-dspform.component.html',
  styleUrls: ['./non-dspform.component.css']
})
export class NonDSPformComponent implements OnInit {

  constructor(private sendFormNotDSP: SendFormDataService) { }

  ngOnInit() { }

  json = formJson

  sendDataNotDSP(result) {
    this.sendFormNotDSP.sendFormData(result).subscribe((res) => {
      console.log('Form sent');
    },
      (res) => {
      });
  }

}
