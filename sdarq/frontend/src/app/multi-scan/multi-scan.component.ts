import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { ScanServiceService } from '../services/scan-service.service';
import { CisProjectService } from '../services/cis-project.service';

@Component({
  selector: 'app-multi-scan',
  templateUrl: './multi-scan.component.html',
  styleUrls: ['./multi-scan.component.css']
})
export class MultiScanComponent implements OnInit {

  json = formJson
  showModalErrService: boolean;
  showModalErrProject: boolean;
  showForm: boolean;
  showModalErrorServiceScan: any;
  showModalErrorProjectScan: any;

  constructor(private projectScan: CisProjectService, private servicescan: ScanServiceService) { }

  ngOnInit(): void {
    this.showModalErrorServiceScan = false;
    this.showModalErrorProjectScan = false;
    this.showForm = true;
  }

  requestMultiScan(result) {
    this.projectScan.sendCisProject(result).subscribe((res) => {
    },
      (res) => {
        this.showModalErrProject = true;
        this.showModalErrorProjectScan = res;
        this.showForm = false;
      });

    this.servicescan.sendServiceScanrRequest(result).subscribe((res1) => {
    },
      (res1) => {
        this.showModalErrService = true;
        this.showModalErrorServiceScan = res1;
        this.showForm = false;
      });
  }
}
