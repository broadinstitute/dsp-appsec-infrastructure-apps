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
  table_show: boolean;
  json = formJson

  constructor(private sendProject: CisProjectService, private http: HttpClient) { }

  ngOnInit(): void { }
  sendData(result) {
    if (result.slack_channel) {
      this.sendProject.sendCisProject(result).subscribe((data: any) => { },
        (data) => {
          console.log("Sent")
        });
    } else {
      this.sendProject.sendCisProject(result).subscribe((data: any) => {
        if (!result.slack_channel && data.status == 'true') {
          location.href = location.origin + '/cis/results?project_id=' + result.project_id;
        }
      },
        (data) => {
          console.log("Not sent")
        });
    }
  }
}