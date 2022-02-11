import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { EditSecurityControlsService } from '../services/edit-service-security-controls/edit-security-controls.service';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';

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

  constructor(private getSecurityControls: GetServiceSecurityControlsService, private editSecurityControls: EditSecurityControlsService) { }

  ngOnInit(): void {
    this.chooseServiceToEditForm = true;
    this.serviceToEditForm = false;
    this.showModalError = false;
  }

  chooseServiceForm = new FormGroup({
    service: new FormControl('', [Validators.required, Validators.minLength(3), Validators.maxLength(15)]),
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
    },
    (serviceSecurityControl) => {
      this.errorMessage = serviceSecurityControl;
      this.showModalError = true;
      this.serviceToEditForm = false;
      this.showServiceData = false;
    });
  }


  onSubmit(result) {
    result['service'] = this.service
    this.showServiceData = false;
    this.editSecurityControls.editSCT(result).subscribe((data: any) => {
    },
      (data) => {
        this.errorMessage = data;
        this.showModalError = true;
        this.serviceToEditForm = false;
        this.showServiceData = false;
      });
  }
}


