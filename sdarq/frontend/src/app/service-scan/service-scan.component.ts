import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { ScanServiceService } from '../services/scan-service/scan-service.service';


@Component({
  selector: 'app-service-scan',
  templateUrl: './service-scan.component.html',
  styleUrls: ['./service-scan.component.css']
})
export class ServiceScanComponent implements OnInit {

  showModalErr: boolean;
  showForm: boolean;
  showModalError: any;

  constructor(private sendServiceScanrRequest: ScanServiceService) { }

  ngOnInit(): void {
    this.showModalErr = false;
    this.showForm = true;
  }

  json = formJson

  requestServiceScan(result) {
    this.sendServiceScanrRequest.sendServiceScanrRequest(result).subscribe((res) => {
    },
      (res) => {
        this.showModalErr = true;
        this.showModalError = res;
        this.showForm = false;
      });
  }
}
