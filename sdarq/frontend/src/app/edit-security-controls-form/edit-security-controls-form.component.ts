import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { EditSecurityControlsService } from '../services/edit-service-security-controls/edit-security-controls.service';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';
import { Clipboard } from '@angular/cdk/clipboard';
import formJson from './form.json';


@Component({
  selector: 'app-edit-security-controls-form',
  templateUrl: './edit-security-controls-form.component.html',
  styleUrls: ['./edit-security-controls-form.component.css']
})
export class EditSecurityControlsFormComponent implements OnInit {
  json = formJson;
  answers: object;
  service: string;
  data: any;
  chooseServiceToEditForm: boolean;
  serviceToEditForm: boolean;
  choosenService: string;
  showModalError: boolean;
  errorMessage: string;

  constructor(private getSecurityControls: GetServiceSecurityControlsService,
              private editSecurityControls: EditSecurityControlsService,
              private clipboard: Clipboard,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) {
                // This is intentional
              }

  ngOnInit(): void {
    this.chooseServiceToEditForm = true;
    this.serviceToEditForm = false;
    this.showModalError = false;
  }

  chooseServiceForm = new FormGroup({
    service: new FormControl('', [Validators.required, Validators.minLength(3), Validators.maxLength(30)]),
  })


  editService() {
    this.loadSecurityControls(this.chooseServiceForm.value)
    this.chooseServiceToEditForm = false;
    this.showModalError = false;
    this.serviceToEditForm = true;
  }

  loadSecurityControls(serviceName) {
    this.getSecurityControls.getServiceSecurityControls(serviceName).subscribe((serviceSecurityControl) => {
        this.answers = serviceSecurityControl;
        this.service = serviceSecurityControl.service;
      },
      (serviceSecurityControl) => {
        this.ngZone.run(() => {
        this.errorMessage = serviceSecurityControl;
        this.showModalError = true;
        this.serviceToEditForm = false;
      });
    });
  }


  onSubmit(result) {
    result['service'] = this.service
    this.editSecurityControls.editSCT(result).subscribe(() => {
      this.ref.detectChanges();
    },
      (data) => {
        this.ngZone.run(() => {
        this.errorMessage = data;
        this.showModalError = true;
        this.serviceToEditForm = false;
      });
    });
  }
}