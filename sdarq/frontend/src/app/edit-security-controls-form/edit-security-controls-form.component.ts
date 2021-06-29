import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';
import { GetSecurityControlsService } from '../services/get-security-controls.service';
import { ServiceSecurityControl } from '../models/service-security-control.model';
import { EditSecurityControlsService } from '../services/edit-security-controls.service';

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
  CodeDx: string;
  defect_dojo: string;
  zap: boolean;
  sourceclear: boolean;
  sourceclear_link: string;
  docker_scan: boolean;
  cis_scanner: boolean;
  burp: boolean;
  securityControls: any;
  data: any;
  item: any;
  chooseServiceToEditForm: boolean;
  serviceToEditForm: boolean;
  serviceName: string;
  choosenService: string;


  constructor(private getSecurityControls: GetSecurityControlsService, private editSecurityControls: EditSecurityControlsService) { }

  ngOnInit(): void {
    this.chooseServiceToEditForm = true;
    this.serviceToEditForm = false;
  }

  chooseServiceForm = new FormGroup({
    serviceName: new FormControl(''),
  })

  editService() {
    const choosenService = this.chooseServiceForm.value.serviceName
    this.loadSecurityControls(choosenService)
    this.chooseServiceToEditForm = false;
    this.serviceToEditForm = true;
  }

  loadSecurityControls(choosenService) {
    this.getSecurityControls.getAllSecurityControls().subscribe((serviceSecurityControl: ServiceSecurityControl[]) => {
      this.securityControls = serviceSecurityControl;
      this.data = this.getSecurityControlForService(this.securityControls, choosenService)
      return this.data
    })
  }

  getSecurityControlForService(securityControls, choosenService) {
    // tslint:disable-next-line
    for (let item of securityControls) {
      if (item.service === choosenService) {
        this.setValue(item)
        return item;
      }
    }
  }

  setValue(item) {
    this.securityControlForm.get('product').setValue(item.product)
    this.securityControlForm.get('service').setValue(item.service)
    this.securityControlForm.get('github').setValue(item.github)
    this.securityControlForm.get('dev_url').setValue(item.dev_url)
    this.securityControlForm.get('CodeDx').setValue(item.CodeDx)
    this.securityControlForm.get('defect_dojo').setValue(item.defect_dojo)
    this.securityControlForm.get('zap').setValue(item.zap)
    this.securityControlForm.get('sourceclear').setValue(item.sourceclear)
    this.securityControlForm.get('sourceclear_link').setValue(item.sourceclear_link)
    this.securityControlForm.get('docker_scan').setValue(item.docker_scan)
    this.securityControlForm.get('cis_scanner').setValue(item.cis_scanner)
    this.securityControlForm.get('burp').setValue(item.burp)
  }

  securityControlForm = new FormGroup({
    product: new FormControl(''),
    service: new FormControl(''),
    github: new FormControl(''),
    dev_url: new FormControl(''),
    CodeDx: new FormControl(''),
    defect_dojo: new FormControl(''),
    zap: new FormControl(''),
    sourceclear: new FormControl(''),
    sourceclear_link: new FormControl(''),
    docker_scan: new FormControl(''),
    cis_scanner: new FormControl(''),
    burp: new FormControl(''),
  });

  onSubmit() {
    this.editSecurityControls.editSCT(this.securityControlForm.value).subscribe((data: any) => {
    },
      (data) => {
      });
  }
}


