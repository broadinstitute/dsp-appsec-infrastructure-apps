import {
  Component,
  OnInit
} from '@angular/core';
import {
  FormGroup,
  FormControl,
  Validators
} from '@angular/forms';
import {
  EditSecurityControlsService
} from '../services/edit-service-security-controls/edit-security-controls.service';
import {
  GetServiceSecurityControlsService
} from '../services/get-service-security-controls/get-service-security-controls.service';
import {
  Clipboard
} from '@angular/cdk/clipboard';

import formJson from './form.json';


@Component({
  selector: 'app-edit-security-controls-form',
  templateUrl: './edit-security-controls-form.component.html',
  styleUrls: ['./edit-security-controls-form.component.css']
})
export class EditSecurityControlsFormComponent implements OnInit {
  product: string;
  service: string;
  github: string;
  security_champion: string;
  dev_url: string;
  vulnerability_management: string;
  defect_dojo: string;
  zap: boolean;
  sourceclear: boolean;
  sourceclear_link: string;
  docker_scan: boolean;
  cis_scanner: boolean;
  burp: boolean;
  security_pentest_link: string;
  threat_model: boolean;
  threat_model_link: string;
  sast: boolean;
  data: any;
  item: any;
  chooseServiceToEditForm: boolean;
  serviceToEditForm: boolean;
  showServiceData: boolean;
  choosenService: string;
  json = formJson;
  datas: any;
  showModalError: boolean;
  errorMessage: string;

  constructor(private getSecurityControls: GetServiceSecurityControlsService, private editSecurityControls: EditSecurityControlsService, private clipboard: Clipboard) {}

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
        this.product = serviceSecurityControl.product;
        this.service = serviceSecurityControl.service;
        this.security_champion = serviceSecurityControl.security_champion
        this.github = serviceSecurityControl.github;
        this.dev_url = serviceSecurityControl.dev_url;
        this.vulnerability_management = serviceSecurityControl.vulnerability_management;
        this.defect_dojo = serviceSecurityControl.defect_dojo;
        this.threat_model = serviceSecurityControl.threat_model;
        this.threat_model_link = serviceSecurityControl.threat_model_link;
        this.zap = serviceSecurityControl.zap;
        this.sourceclear = serviceSecurityControl.sourceclear;
        this.sourceclear_link = serviceSecurityControl.sourceclear_link;
        this.docker_scan = serviceSecurityControl.docker_scan;
        this.cis_scanner = serviceSecurityControl.cis_scanner;
        this.burp = serviceSecurityControl.burp;
        this.security_pentest_link = serviceSecurityControl.security_pentest_link;
        this.sast = serviceSecurityControl.sast;
      },
      (serviceSecurityControl) => {
        this.errorMessage = serviceSecurityControl;
        this.showModalError = true;
        this.serviceToEditForm = false;
        this.showServiceData = false;
      });
  }

  copyProductName() {
    const pending =
      this.clipboard.beginCopy(this.product);
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
  copySecChamp() {
    const pending =
      this.clipboard.beginCopy(this.security_champion);
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

  copyGithubUrl() {
    const pending =
      this.clipboard.beginCopy(this.github);
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

  copyDefectDojoUrl() {
    const pending =
      this.clipboard.beginCopy(this.defect_dojo);
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

  copyVMLink() {
    const pending =
      this.clipboard.beginCopy(this.vulnerability_management);
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

  copySourcelearLink() {
    const pending =
      this.clipboard.beginCopy(this.sourceclear_link);
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
    this.editSecurityControls.editSCT(result).subscribe((data) => {},
      (data) => {
        this.errorMessage = data;
        this.showModalError = true;
        this.serviceToEditForm = false;
        this.showServiceData = false;
      });
  }
}