import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { SendFormDataService } from '../services/create-new-service/send-form-data.service';
import formJson from './form.json';

@Component({
  selector: 'app-app-form',
  templateUrl: './app-form.component.html',
  styleUrls: ['./app-form.component.css']
})
export class AppFormComponent implements OnInit {

  errors: string;
  json = formJson
  showAlert: boolean;
  showForm: boolean;

  constructor(private sendForm: SendFormDataService,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) { }

  ngOnInit(): void {
  }

  sendData(result) {
    this.sendForm.sendFormData(result).subscribe(() => {
      this.ref.detectChanges();
    },
      (submitNewServiceQuestionnaireResponse) => {
        this.ngZone.run(() => {
        this.showAlert = true;
        this.showForm = false;
        this.errors = submitNewServiceQuestionnaireResponse;
      });
    });
}
}
