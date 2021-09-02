import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { GetSecurityControlsService } from '../services/get-security-controls.service';
import { ServiceSecurityControl } from '../models/service-security-control.model';
import { EditSecurityControlsService } from '../services/edit-security-controls.service';
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
  dev_url: string;
  vulnerability_management: string;
  defect_dojo: string;
  zap: boolean;
  sourceclear: boolean;
  sourceclear_link: string;
  docker_scan: boolean;
  cis_scanner: boolean;
  burp: boolean;
  data: any;
  item: any;
  chooseServiceToEditForm: boolean;
  serviceToEditForm: boolean;
  showServiceData: boolean;
  serviceName: string;
  choosenService: string;
  secControls: any;
  json = formJson;

  constructor(private getSecurityControls: GetSecurityControlsService, private editSecurityControls: EditSecurityControlsService) { }

  ngOnInit(): void {
    this.chooseServiceToEditForm = true;
    this.serviceToEditForm = false;
  }

  chooseServiceForm = new FormGroup({
    serviceName: new FormControl('', [Validators.required, Validators.minLength(3), Validators.maxLength(15)]),
  })


  editService() {
    const choosenService = this.chooseServiceForm.value.serviceName
    this.loadSecurityControls(choosenService)
    this.chooseServiceToEditForm = false;
    this.serviceToEditForm = true;
    this.showServiceData = true;
  }

  loadSecurityControls(choosenService) {
    this.getSecurityControls.getAllSecurityControls().subscribe((serviceSecurityControl: ServiceSecurityControl[]) => {
      for (const item of serviceSecurityControl) {
        if (item.service === choosenService) {
            this.secControls = item;
            this.product = item.product;
            this.service = item.service;
            this.github = item.github;
            this.dev_url = item.dev_url;
            this.vulnerability_management = item.vulnerability_management;
            this.defect_dojo = item.defect_dojo;
            this.zap = item.zap;
            this.sourceclear = item.sourceclear;
            this.sourceclear_link = item.sourceclear_link;
            this.docker_scan = item.docker_scan;
            this.cis_scanner = item.cis_scanner;
            this.burp = item.burp;
        }
      }
    })
  }


  onSubmit(result) {
    result['service'] = this.service
    this.showServiceData = false;
    this.editSecurityControls.editSCT(result).subscribe((data: any) => {
    },
      (data) => {
        console.log(data)
      });
  }
}


