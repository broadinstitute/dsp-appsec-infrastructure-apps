import { Component, OnInit } from '@angular/core';
import { CisProjectService } from '../services/cis-project.service';
import { HttpClient } from '@angular/common/http';
import { GetCisScanService} from '../services/get-cis-scan.service';
import formJson from './form.json';

@Component({
  selector: 'app-cis',
  templateUrl: './cis.component.html',
  styleUrls: ['./cis.component.css']
})
export class CisComponent implements OnInit {

  projectFindings: any[];
  data: any[] = [];
  table_show: boolean;
  json = formJson

  constructor(private sendProject: CisProjectService, private http: HttpClient, private getProjectScan: GetCisScanService) { }

  ngOnInit() { }

  sendData(result) {
    // this.sendProject.sendCisProject(result).subscribe((data: any ) => {
    //   //  this.projectFindings = data;
    //   // this.table_show = true;
    // },
    //     (data) => {
    //       console.log("Not sent")
    //     });
    // this.getProjectScan.getCisScan(result.project_id).subscribe((data: any) => {
    //   this.projectFindings = data;
    //   this.table_show = true;
    //  },
    //     (data) => {
    //       console.log("Not sent")
    //     });
    location.href = 'http://127.0.0.1:4200/cis/results?project_id=' + result.project_id;
}
}

