import { Component, OnInit } from '@angular/core';
import { SendFormDataService } from '../send-form-data.service';
import { HttpClient } from '@angular/common/http';
import  formJson from './newForm.json';

@Component({
  selector: 'app-non-dspform',
  templateUrl: './non-dspform.component.html',
  styleUrls: ['./non-dspform.component.css']
})
export class NonDSPformComponent implements OnInit {

   constructor(private sendFormNotDSP: SendFormDataService, private http: HttpClient) { }

   ngOnInit() {}

  json = formJson

  sendDataNotDSP(result) {
      this.sendFormNotDSP.sendFormData(result).subscribe((res) => {
          console.log('Form sent');
        },
        (res) => {
        });
    }

}
