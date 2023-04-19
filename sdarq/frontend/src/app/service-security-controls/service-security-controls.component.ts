import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { GetServiceSecurityControlsService } from '../services/get-service-security-controls/get-service-security-controls.service';
import { ActivatedRoute } from '@angular/router';
import { ServiceSecurityControl } from '../models/service-security-control.model';


@Component({
  selector: 'app-service-security-controls',
  templateUrl: './service-security-controls.component.html',
  styleUrls: ['./service-security-controls.component.css']
})
export class ServiceSecurityControlsComponent implements OnInit {
  serviceSecurityControl: ServiceSecurityControl[];

  errorMessage: any;
  showServiceData: boolean;
  showModalError: boolean;
  showSpinner: boolean;
  value: string;
  errors: string;
  valuejson: {};
  headElements = ['Security Control', 'State']
  data: any;
  service: string;
  product: string;
  burp: boolean;
  security_pentest_link: string;
  cis_scanner: boolean;
  dev_url: string;
  github: string;
  sourceclear: boolean;
  sourceclear_link: string;
  threat_model: boolean;
  threat_model_link: string;
  docker_scan: boolean;
  zap: boolean;
  vulnerability_management: string;
  defect_dojo: string;
  sast: boolean;
  sast_link: string;

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
        this.sast_link = serviceSecurityControl.sast_link;
        this.github = serviceSecurityControl.github;
        this.sourceclear = serviceSecurityControl.sourceclear;
        this.vulnerability_management = serviceSecurityControl.vulnerability_management;
        this.product = serviceSecurityControl.product;
        this.sourceclear_link = serviceSecurityControl.sourceclear_link;
        this.sast = serviceSecurityControl.sast;
        this.zap = serviceSecurityControl.zap;
        this.defect_dojo = serviceSecurityControl.defect_dojo;
        this.service = serviceSecurityControl.service;
        this.dev_url = serviceSecurityControl.dev_url;
        this.threat_model = serviceSecurityControl.threat_model;
        this.threat_model_link = serviceSecurityControl.threat_model_link;
        this.docker_scan = serviceSecurityControl.docker_scan;
        this.cis_scanner = serviceSecurityControl.cis_scanner;
        this.burp = serviceSecurityControl.burp;
        this.security_pentest_link = serviceSecurityControl.security_pentest_link;
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