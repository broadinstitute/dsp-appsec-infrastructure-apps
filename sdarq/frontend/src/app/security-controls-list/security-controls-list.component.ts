import { Component, NgZone, OnInit } from '@angular/core';
import { GetSecurityControlsService } from '../services/get-all-security-controls/get-security-controls.service'
import { ServiceSecurityControl } from '../models/service-security-control.model';


@Component({
  selector: 'app-security-controls-list',
  templateUrl: './security-controls-list.component.html',
  styleUrls: ['./security-controls-list.component.css']
})
export class SecurityControlsListComponent implements OnInit {

  serviceSecurityControl: ServiceSecurityControl[];
  // tslint:disable-next-line
  headElements = ['Service', 'Product', 'Dev URL', 'Sourcecode', 'DefectDojo', 'Threat Model', 'Container Image Scan', 'Manual Pentest', 'DAST', 'SAST', 'CIS scan', 'Dependecies scan'];

  sourceclear_results: boolean;
  zap_results: boolean;
  sast_results: boolean;
  dev_link: boolean;
  security_pentest: boolean;
  threat_model_results: boolean;
  searchString: any;
  errorMessage: string;
  showModalError: boolean;
  showSearch: boolean;
  showTable: boolean;


  constructor(private getSecurityControls: GetSecurityControlsService,  private ngZone: NgZone) {
    // This is intentional
   }

  ngOnInit() {
    this.showModalError = false;
    this.showSearch = true;
    this.showTable = true;
    this.getResults()
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

  threatmodelShowValue(threat_model) {
    if (threat_model === true) {
      this.threat_model_results = true;
    } else {
      this.threat_model_results = false;
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
      return '<a href="#" data-mdb-toggle="tooltip" title="Not applicable for this service"><i class="fas fa-info-circle blue-color fa-2x"></i><a>'
    } else {
      this.dev_link = true;
    }
  }

  getResults() {
    this.getSecurityControls.getAllSecurityControls().subscribe((serviceSecurityControl: ServiceSecurityControl []) => {
      this.serviceSecurityControl = serviceSecurityControl;
    },
      (serviceSecurityControl) => {
        this.ngZone.run(() => {
        this.errorMessage = serviceSecurityControl;
        this.showModalError = true;
        this.showSearch = false;
        this.showTable = false;
      }); 
      });
  }
}


