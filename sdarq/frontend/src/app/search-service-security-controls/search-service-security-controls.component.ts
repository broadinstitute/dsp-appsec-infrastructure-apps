import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import formJson from './form.json';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';


@Component({
  selector: 'app-search-service-security-controls',
  templateUrl: './search-service-security-controls.component.html',
  styleUrls: ['./search-service-security-controls.component.css']
})
export class SearchServiceSecurityControlsComponent implements OnInit {

  json = formJson;
  showForm: boolean;
  showModalErr: boolean;

  constructor(private getSecurityControls: GetServiceSecurityControlsService,
    private ref: ChangeDetectorRef,
    private ngZone: NgZone) {}

  ngOnInit(): void {
    this.showForm = true;
    this.showModalErr = false;
  }

  sendData(result) {
    this.getSecurityControls.getServiceSecurityControls(result).subscribe((data) => {
        this.ref.detectChanges();
        location.href = location.origin + '/service-security-controls/results?servicename=' + result.service;
      },
      (data) => {
        this.ngZone.run(() => {
          this.showModalErr = data;
        });
      });
  }
}