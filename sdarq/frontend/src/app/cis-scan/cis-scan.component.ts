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

  constructor(private sendProject: CisProjectService, private http: HttpClient) { }

  ngOnInit(): void { }

  sendData(result) {
    if (result.slack_channel) {
      this.sendProject.sendCisProject(result).subscribe((data: any) => {
        console.log('Notification sent to slack')
      });
    } else {
      this.sendProject.sendCisProject(result).subscribe((data: any) => {
        location.href = location.origin + '/cis/results?project_id=' + result.project_id;
      });
    }
  }
}
