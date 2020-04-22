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

  ngOnInit(): void {
  }
  sendData(result) {
    if (result.slack_channel) { 
    this.sendProject.sendCisProject(result).subscribe((data: any ) => {
    },
        (data) => {
          console.log("Not sent")
        });

      }
    else {
      this.sendProject.sendCisProject(result).subscribe((data: any ) => {
      },
          (data) => {
            console.log("Not sent")
          }); 
     location.href = 'http://127.0.0.1:4200/cis/results?project_id=' + result.project_id;
    }
}
}
