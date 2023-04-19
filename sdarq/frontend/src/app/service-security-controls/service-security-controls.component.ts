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
  data = [{
    "sast_link": "https://sonarcloud.io/project/overview?id=broadinstitute_sam",
    "dev_url": "https://sam.dsde-dev.broadinstitute.org/https://sam.dsde-dev.broadinstitute.org/",
    "github": "https://github.com/broadinstitute/sam",
    "sourceclear": "True",
    "cis_scanner": "True",
    "burp": "True",
    "vulnerability_management": "https://defectdojo.dsp-appsec.broadinstitute.org//product/181/finding/open?test_import_finding_action__test_import=&title=&component_name=&component_version=&date=&last_reviewed=&last_status_update=&mitigated=&test__test_type=158&test__engagement__version=&test__version=&status=&active=unknown&verified=unknown&duplicate=&is_mitigated=&out_of_scope=unknown&false_p=unknown&risk_accepted=unknown&has_component=unknown&has_notes=unknown&file_path=&unique_id_from_tool=&vuln_id_from_tool=&service=&param=&payload=&risk_acceptance=&has_finding_group=unknown&tags=&test__tags=&test__engagement__tags=&test__engagement__product__tags=&tag=&not_tags=&not_test__tags=&not_test__engagement__tags=&not_test__engagement__product__tags=&not_tag=&vulnerability_id=&planned_remediation_date=&endpoints__host=&o=",
    "product": "Terra",
    "threat_model": "True",
    "sourceclear_link": "https://defectdojo.dsp-appsec.broadinstitute.org//product/181/finding/open?test_import_finding_action__test_import=&title=&component_name=&component_version=&date=&last_reviewed=&last_status_update=&mitigated=&reporter=17&test__engagement__version=&test__version=&status=&active=unknown&verified=unknown&duplicate=&is_mitigated=&out_of_scope=unknown&false_p=unknown&risk_accepted=unknown&has_component=unknown&has_notes=unknown&file_path=&unique_id_from_tool=&vuln_id_from_tool=&service=&param=&payload=&risk_acceptance=&has_finding_group=unknown&tags=&test__tags=&test__engagement__tags=&test__engagement__product__tags=&tag=&not_tags=&not_test__tags=&not_test__engagement__tags=&not_test__engagement__product__tags=&not_tag=&vulnerability_id=&planned_remediation_date=&endpoints__host=&o=",
    "sast": true,
    "zap": "True",
    "security_pentest_link": "https://docs.google.com/document/d/1Kc_CTlTwkaJvTG94pmFRUcPC2Gl25gz7wTtEZe3B_9Q/edit#heading=h.rvpr6zoz0jem",
    "service": "Sam",
    "docker_scan": "True",
    "defect_dojo": "https://defectdojo.dsp-appsec.broadinstitute.org/product/181"
}]
  serviceSecurityControl: { sast_link: string; dev_url: string; github: string; sourceclear: string; cis_scanner: string; burp: string; vulnerability_management: string; product: string; threat_model: string; sourceclear_link: string; sast: boolean; zap: string; security_pentest_link: string; service: string; docker_scan: string; defect_dojo: string; }[];


  constructor(private getSecurityControls: GetServiceSecurityControlsService,
    private ngZone: NgZone,
    private router: ActivatedRoute,
    private ref: ChangeDetectorRef) {
    // This is intentional 
  }

  ngOnInit(): void {
    this.serviceSecurityControl = this.data
    console.log(this.serviceSecurityControl)
    // this.showSpinner = true;
    // this.router.queryParams.subscribe(params => {
    //   this.value = params.servicename
    //   this.valuejson = {
    //     'service': this.value
    //   }
    //   // this.getResults(this.valuejson)
    // })
  }

  // private getResults(valuejson) {
  //   this.getSecurityControls.getServiceSecurityControls(this.valuejson).subscribe((serviceSecurityControl) => {
  //       this.ref.detectChanges();
  //       this.showSpinner = false;
  //       this.data = serviceSecurityControl
  //       console.log(this.data)
  //     },
  //     (serviceSecurityControl) => {
  //       this.ngZone.run(() => {
  //         this.showModalError = true;
  //         this.errors = serviceSecurityControl;
  //         this.showSpinner = false;
  //         console.log(serviceSecurityControl)
  //       });
  //     });
  // }
}