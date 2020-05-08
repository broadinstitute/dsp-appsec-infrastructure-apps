import { Component, OnInit } from '@angular/core';
import { CisProjectService } from '../services/cis-project.service';
import { HttpClient } from '@angular/common/http';
import { GetCisScanService } from '../services/get-cis-scan.service';
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
    location.href = location.origin + '/cis/results?project_id=' + result.project_id;
  }
}
