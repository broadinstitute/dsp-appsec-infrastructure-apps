import { SendFormDataService } from '../services/create-new-service/send-form-data.service';
import { CisProjectService } from '../services/scan-gcp-project/cis-project.service';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';
import formJson from './form.json';
import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';


@Component({
  selector: 'app-terra-new-service',
  templateUrl: './terra-new-service.component.html',
  styleUrls: ['./terra-new-service.component.css']
})
export class TerraNewServiceComponent implements OnInit {

  errors: string;
  json = formJson
  arrRequired = {};
  showAlert: boolean;
  showForm: boolean;

  constructor(private sendForm: SendFormDataService,
    private scanGCPproject: CisProjectService,
    private createNewSctService: CreateNewSctService,
    private ngZone: NgZone,
    private ref: ChangeDetectorRef) { 
      // This is intentional
    }

    ngOnInit() {
      this.showForm = true;
    }
  
    sendData(result) {
      this.sendForm.sendFormData(result).subscribe(() => {
        this.ref.detectChanges();
      },
        (submitNewServiceQuestionnaireResponse) => {
          this.ngZone.run(() => {
          this.showAlert = true;
          this.showForm = false;
          this.errors = submitNewServiceQuestionnaireResponse;
        });
      });
  
      this.arrRequired = {
        'service': result['Service'],
        'github': result['Github URL'],
        'product': result['Product'],
        'dev_url': '',
        'burp': false,
        'zap': false,
        'cis_scanner': false,
        'sourceclear': false,
        'docker_scan': false,
        'threat_model': false,
        'sast': false
      };
      
      this.createNewSctService.createNewSCT(this.arrRequired).subscribe((createNewSCTResponse) => {
        console.log("Security Controls template created for this service")
      });
  
      if (result.project_id) {
        this.scanGCPproject.sendCisProject(result).subscribe((scanGCPProjectResponse) => {
          console.log("CIS scanner running against GCP project")
        });
      }
    }
  }
  