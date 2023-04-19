import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-service-security-controls',
  templateUrl: './service-security-controls.component.html',
  styleUrls: ['./service-security-controls.component.css']
})
export class ServiceSecurityControlsComponent implements OnInit {
  errorMessage: any;
  showServiceData: boolean;
  showModalError: boolean;
  showSpinner: boolean;
  value: string;
  errors: string;
  valuejson: {};
  headElements = ['Security Control', 'State']
  data: any;

  constructor(private getSecurityControls: GetServiceSecurityControlsService,
    private ngZone: NgZone,
    private router: ActivatedRoute,
    private ref: ChangeDetectorRef) {
    // This is intentional 
  }

  ngOnInit(): void {
    this.router.queryParams.subscribe(params => {
      this.value = params.servicename
      this.valuejson = {
        'service': this.value
      }
      this.getResults(this.valuejson)
    })
  }

  private getResults(valuejson) {
    this.getSecurityControls.getServiceSecurityControls(this.valuejson).subscribe((serviceSecurityControl) => {
        this.ref.detectChanges();
        this.showSpinner = false;
        this.data = serviceSecurityControl
        console.log(this.data)
      },
      (serviceSecurityControl) => {
        this.ngZone.run(() => {
          this.showModalError = true;
          this.errors = serviceSecurityControl;
          this.showSpinner = false;
          console.log(serviceSecurityControl)
        });
      });
  }
}