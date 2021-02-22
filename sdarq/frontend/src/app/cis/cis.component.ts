import { Component, OnInit } from '@angular/core';
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

  constructor() { }

  ngOnInit() { }

  sendData(result) {
    location.href = location.origin + '/cis/results?project_id=' + result.project_id;
  }
}
