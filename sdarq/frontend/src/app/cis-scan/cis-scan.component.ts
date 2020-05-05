import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { CisProjectService } from '../services/cis-project.service';
import { HttpClient } from '@angular/common/http';


@Component({
  selector: 'app-cis-scan',
  templateUrl: './cis-scan.component.html',
  styleUrls: ['./cis-scan.component.css']
})
export class CisScanComponent implements OnInit {

  projectFindings: any[];
  data: any[] = [];
  json = formJson
  showModal: boolean;
  errors: any[];
  showPage: boolean;

  constructor(private sendProject: CisProjectService, private http: HttpClient) { }

  ngOnInit(): void { this.showModal = false; this.showPage = true; }

  sendData(result) {
    if (result.slack_channel) {
      this.sendProject.sendCisProject(result).subscribe((data: any) => {
        if (data.status === 'false' && data.statusCode === '404') {
          this.errors = data
          this.showModal = true;
          this.showPage = false;
        } else if (data.status === 'true') {
          console.log('Notification sent to slack')
        }
      },
        (data) => {
          console.log('Not sent')
        });
    } else {
      this.sendProject.sendCisProject(result).subscribe((data: any) => {
        if (!result.slack_channel && data.status === 'true') {
          location.href = location.origin + '/cis/results?project_id=' + result.project_id;
        } else if (!result.slack_channel && data.status === 'false' && data.statusCode === '404') {
          this.errors = data
          this.showModal = true;
          this.showPage = false;
        }
      },
        (data) => {
          console.log('Not sent')
        });
    }
  }
}
