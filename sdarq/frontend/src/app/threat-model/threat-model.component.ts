import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
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
  showModalErr: boolean;
  showModalError: any;

  constructor(private sendForm: RequestTmService,
              private http: HttpClient,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) {
                // This is intentional
               }

  ngOnInit(): void {
    this.showForm = true;
    this.showModalErr = false;
  }

  json = formJson

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe(() => {
      this.ref.detectChanges();
      this.showForm = true;
      this.showModalErr = false;
    },
      (res) => { 
        this.ngZone.run(() => {
        this.showForm = false;
        this.showModalErr = true;
        this.showModalError = res;
      });
    });
  }
}
