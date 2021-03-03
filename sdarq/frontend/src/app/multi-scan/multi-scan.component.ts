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

  constructor(private projectScan: CisProjectService, private servicescan: ScanServiceService) { }

  ngOnInit(): void {
  }

  requestMultiScan(result) {
    this.projectScan.sendCisProject(result).subscribe((res) => {
    },
      (res) => {});

    this.servicescan.sendServiceScanrRequest(result).subscribe((res1) => {
    },
      (res1) => {});
  }
}
