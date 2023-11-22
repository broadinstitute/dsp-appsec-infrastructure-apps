import { Component, OnInit, NgZone } from '@angular/core';
import formJson from './form.json';
import { CisProjectService } from '../services/scan-gcp-project/cis-project.service';


@Component({
  selector: 'app-cis-scan',
  templateUrl: './cis-scan.component.html',
  styleUrls: ['./cis-scan.component.css']
})
export class CisScanComponent implements OnInit {

  projectFindings: any[];
  data: any[] = [];
  json = formJson;
  showSpinner: boolean;
// showModal: boolean;
  showForm: boolean;
  showModalErr: boolean;
  showModalError: string;

  constructor(private sendProject: CisProjectService, private ngZone: NgZone) {
    // This is intentional
   }

  ngOnInit(): void {
    // this.showModal = false;
    this.showForm = true;
    this.showModalErr = false;
  }

  sendData(result) {
      this.sendProject.sendCisProject(result).subscribe((data) => {
        // this.showModal = true;
        this.showForm = false;
        this.showSpinner = false;
      },
      (data) => {
        this.ngZone.run(() => {
        // this.showModal = false;
        this.showModalErr = true;
        this.showModalError = data;
        this.showForm = false;
        this.showSpinner = false;
      });
    });
    }
}
