import { Component, OnInit } from '@angular/core';
import { GetSecurityControlsService } from '../services/get-security-controls.service'
import { ActivatedRoute } from '@angular/router';
import { ServiceSecurityControl } from '../models/service-security-control.model';
import { BooleanLiteral } from 'typescript';


@Component({
  selector: 'app-security-controls-list',
  templateUrl: './security-controls-list.component.html',
  styleUrls: ['./security-controls-list.component.css']
})
export class SecurityControlsListComponent implements OnInit {

  serviceSecurityControl: ServiceSecurityControl[];
  // tslint:disable-next-line
  headElements = ['Service', 'Product', 'Dev Url', 'Sourcecode', 'CodeDX', 'DefectDojo', 'Docker scan', 'Manual pentest', 'DAST', 'CIS scan', 'Dependecies scan'];
  sourceclear_results: boolean;
  searchString: any;

  constructor(private getSecurityControls: GetSecurityControlsService, private router: ActivatedRoute) { }

  ngOnInit() {
    this.getResults()
  }

  trivyShowValue(docker_scan) {
    if (docker_scan === true) {
      return '<i class="fas fa-check fa-1x" ></i>'
    } else {
      return '<i class="fas fa-times fa-1x color"></i>'
    }
  }

  burpShowValue(burp) {
    if (burp === true) {
      return '<i class="fas fa-check fa-1x "></i>'
    } else {
      return '<i class="fas fa-times fa-1x"></i>'
    }
  }

  threatmodelShowValue(threat_model) {
    if (threat_model === true) {
      return '<i class="fas fa-check fa-1x"></i>'
    } else {
      return '<i class="fas fa-times fa-1x"></i>'
    }
  }

  zapShowValue(zap) {
    if (zap === true) {
      return '<i class="fas fa-check fa-1x"></i>'
    } else {
      return '<i class="fas fa-times fa-1x"></i>'
    }
  }

  cisscannerShowValue(cis_scanner) {
    if (cis_scanner === true) {
      return '<i class="fas fa-check fa-1x"></i>'
    } else {
      return '<i class="fas fa-times fa-1x"></i>'
    }
  }

  sourceclearShowValue(sourceclear) {
    if (sourceclear === true) {
      this.sourceclear_results = true;
    } else {
      this.sourceclear_results = false;
      return '<i class="fas fa-times fa-1x"></i>'
    }
  }

  getResults() {
    this.getSecurityControls.getAllSecurityControls().subscribe((serviceSecurityControl) => {
      this.serviceSecurityControl = serviceSecurityControl;
    },
      (serviceSecurityControl) => {
      });
  }
}


