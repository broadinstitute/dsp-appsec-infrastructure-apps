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

  constructor(private getSecurityControls: GetServiceSecurityControlsService,
    private ngZone: NgZone,
    private router: ActivatedRoute,
    private ref: ChangeDetectorRef) {
      // This is intentional }
    }

  ngOnInit(): void {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.servicename
      this.getResults(this.value)
    })
  }

  private getResults(value) {
    this.getSecurityControls.getServiceSecurityControls(this.value).subscribe((serviceSecurityControl) => {
      this.ref.detectChanges();
        this.service = serviceSecurityControl.service;
        this.dev_url = serviceSecurityControl.dev_url;
        this.threat_model = serviceSecurityControl.threat_model;
        this.threat_model_link = serviceSecurityControl.threat_model_link;
        this.docker_scan = serviceSecurityControl.docker_scan;
        this.cis_scanner = serviceSecurityControl.cis_scanner;
        this.burp = serviceSecurityControl.burp;
        this.security_pentest_link = serviceSecurityControl.security_pentest_link;
        this.showSpinner = false;
        this.defect_dojo = serviceSecurityControl.defect_dojo;
        this.github = serviceSecurityControl.github;
        this.product = serviceSecurityControl.product;
        this.sast = serviceSecurityControl.sast;
        this.sast_link = serviceSecurityControl.sast_link;
        this.sourceclear = serviceSecurityControl.sourceclear;
        this.sourceclear_link = serviceSecurityControl.sourceclear_link;
        this.vulnerability_management = serviceSecurityControl.vulnerability_management;
        this.zap = serviceSecurityControl.zap;
    },
      (serviceSecurityControl) => {
        this.ngZone.run(() => {
        this.showModalError = true;
        this.errors = serviceSecurityControl;
        this.showSpinner = false;
      });
    });
  }
}
