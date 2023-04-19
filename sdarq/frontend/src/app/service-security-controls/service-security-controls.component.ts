import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-service-security-controls',
  templateUrl: './service-security-controls.component.html',
  styleUrls: ['./service-security-controls.component.css']
})
export class ServiceSecurityControlsComponent implements OnInit {
  service: string;
  dev_url: string;
  threat_model_link: string;
  threat_model: boolean;
  docker_scan: boolean;
  cis_scanner: boolean;
  burp: boolean;
  security_pentest_link: string;
  errorMessage: any;
  showServiceData: boolean;
  showModalError: boolean;
  showSpinner: boolean;
  value: string;
  errors: string;
  zap: boolean;
  vulnerability_management: string;
  sourceclear_link: string;
  defect_dojo: string;
  github: string;
  product: string;
  sast: boolean;
  sast_link: string;
  sourceclear: boolean;
  valuejson: {};
  headElements = ['Security Control', 'State']
  data: { sast_link: string; dev_url: string; github: string; sourceclear: string; cis_scanner: string; burp: string; vulnerability_management: string; product: string; threat_model: string; sourceclear_link: string; sast: boolean; zap: string; security_pentest_link: string; service: string; docker_scan: string; defect_dojo: string; };


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