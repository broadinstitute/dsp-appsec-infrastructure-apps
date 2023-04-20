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
  security_pentest: boolean;
  threat_model_results: boolean;
  threat_model_results_link: boolean;
  zap_results: boolean;
  sast_results: boolean;
  sourceclear_results: boolean;
  dev_link: boolean;
  product_value: boolean;

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



  trivyShowValue(docker_scan) {
    if (docker_scan === true) {
      return '<i class="fas fa-check-circle light-green-color fa-2x" ></i>'
    } else {
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  burpShowValue(burp) {
    if (burp === true) {
      this.security_pentest = true;
    } else {
      this.security_pentest = false;
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  threatmodelShowValue(threat_model, threat_model_link) {
    if (threat_model === true) {
      if (!threat_model_link){
        this.threat_model_results = true;
        this.threat_model_results_link = false;
      } else {
        this.threat_model_results_link = true;
        this.threat_model_results = false;
      }
    } else {
      this.threat_model_results = false;
      this.threat_model_results_link = false;
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  zapShowValue(zap) {
    if (zap === true) {
      this.zap_results = true;
    } else {
      this.zap_results = false;
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  cisscannerShowValue(cis_scanner) {
    if (cis_scanner === true) {
      return '<i class="fas fa-check-circle light-green-color fa-2x"></i>'
    } else {
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  sastShowValue(sast) {
    if (sast === true) {
      this.sast_results = true;
    } else {
      this.sast_results = false;
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  sourceclearShowValue(sourceclear) {
    if (sourceclear === true) {
      this.sourceclear_results = true;
    } else {
      this.sourceclear_results = false;
      return '<i class="fas fa-times-circle red-color fa-2x"></i>'
    }
  }

  devURLShowValue(dev_url) {
    if (dev_url === '') {
      this.dev_link = false;
      return '<a href="#" data-mdb-toggle="tooltip" title="The URL does not exist!"><i class="fas fa-info-circle blue-color fa-2x"></i><a>'
    } else {
      this.dev_link = true;
    }
  }

  productShowValue(product){
    if (product === '') {
      this.product_value = false;
      return '<a href="#" data-mdb-toggle="tooltip" title="The product name is not available!"><i class="fas fa-info-circle blue-color fa-2x"></i><a>'
    } else {
      this.product_value = true;
    }
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
        });
      });
  }
}