import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { ScanServiceService} from '../services/scan-service.service';


@Component({
  selector: 'app-service-scan',
  templateUrl: './service-scan.component.html',
  styleUrls: ['./service-scan.component.css']
})
export class ServiceScanComponent implements OnInit {

  constructor(private sendServiceScanrRequest: ScanServiceService) { }

  ngOnInit(): void {
  }

  json = formJson

  requestServiceScan(result) {
    this.sendServiceScanrRequest.sendServiceScanrRequest(result).subscribe((res) => {
      console.log('Form sent');
    },
      (res) => { });
  }
}
