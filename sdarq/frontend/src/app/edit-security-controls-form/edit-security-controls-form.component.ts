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
  service: string;
  dev_url: string;
  docker_scan: boolean;
  cis_scanner: boolean;
  burp: boolean;
  security_pentest_link: string;
  threat_model: boolean;
  threat_model_link: string;
  data: any;
  item: any;
  chooseServiceToEditForm: boolean;
  serviceToEditForm: boolean;
  showServiceData: boolean;
  choosenService: string;
  datas: any;
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
    this.showServiceData = true;
  }

  loadSecurityControls(datas) {
    this.getSecurityControls.getServiceSecurityControls(datas).subscribe((serviceSecurityControl) => {
        this.service = serviceSecurityControl.service;
        this.dev_url = serviceSecurityControl.dev_url;
        this.threat_model = serviceSecurityControl.threat_model;
        this.threat_model_link = serviceSecurityControl.threat_model_link;
        this.docker_scan = serviceSecurityControl.docker_scan;
        this.cis_scanner = serviceSecurityControl.cis_scanner;
        this.burp = serviceSecurityControl.burp;
        this.security_pentest_link = serviceSecurityControl.security_pentest_link;
      },
      (serviceSecurityControl) => {
        this.ngZone.run(() => {
        this.errorMessage = serviceSecurityControl;
        this.showModalError = true;
        this.serviceToEditForm = false;
        this.showServiceData = false;
      });
    });
  }


  copyDevUrl() {
    const pending =
      this.clipboard.beginCopy(this.dev_url);
    let remainingAttempts = 3;
    const attempt = () => {
      const result = pending.copy();
      if (!result && --remainingAttempts) {
        setTimeout(attempt);
      } else {
        pending.destroy();
      }
    };
    attempt();
  }


  copyTMLink() {
    const pending =
      this.clipboard.beginCopy(this.threat_model_link);
    let remainingAttempts = 3;
    const attempt = () => {
      const result = pending.copy();
      if (!result && --remainingAttempts) {
        setTimeout(attempt);
      } else {
        pending.destroy();
      }
    };
    attempt();
  }

  copyManualPentestLink() {
    const pending =
      this.clipboard.beginCopy(this.security_pentest_link);
    let remainingAttempts = 3;
    const attempt = () => {
      const result = pending.copy();
      if (!result && --remainingAttempts) {
        setTimeout(attempt);
      } else {
        pending.destroy();
      }
    };
    attempt();
  }

  onSubmit(result) {
    result['service'] = this.service
    this.showServiceData = false;
    this.editSecurityControls.editSCT(result).subscribe(() => {
      this.ref.detectChanges();
    },
      (data) => {
        this.ngZone.run(() => {
        this.errorMessage = data;
        this.showModalError = true;
        this.serviceToEditForm = false;
        this.showServiceData = false;
      });
    });
  }
}