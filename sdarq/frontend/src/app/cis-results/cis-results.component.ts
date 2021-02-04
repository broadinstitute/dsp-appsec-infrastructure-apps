import { Component, OnInit } from '@angular/core';
import { GetCisScanService } from '../services/get-cis-scan.service';
import { ActivatedRoute } from '@angular/router';
import { CsvDataService } from '../services/csv-data.service';
declare var require: any

@Component({
  selector: 'app-cis-results',
  templateUrl: './cis-results.component.html',
  styleUrls: ['./cis-results.component.css']
})
export class CisResultsComponent implements OnInit {


  result: any;
  projectFindings: any[];
  latestDate: any[];
  table_id: any[];
  data: any[];
  date: any[];
  params: any;
  value: string;
  showModal: boolean;
  showSpinner: boolean;
  errors: any[];
  showTable: boolean;
  filename: string;
  table_name: any[];
  modified_date: any[];

  headElements = ['Benchmark', 'Id', 'Level', 'CVSS', 'Title', 'Failures', 'Description', 'Rationale', 'Refs'];
  testi: any;


  constructor(private getProjectScan: GetCisScanService, private router: ActivatedRoute, private csvService: CsvDataService) { }

  ngOnInit() {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.project_id
      this.getResults(this.value)
    })
  }

  saveAsCSV(projectFindings, modified_date, table_name) {
    const format = '.csv'
    const prefix = 'GCP_CIS_Results_'.concat(table_name.toString())
    const table = prefix.concat('_'.toString())
    this.filename = table.concat(modified_date.toString()).concat(format.toString())
    this.csvService.exportToCsv(this.filename, this.ConvertToCSV(JSON.stringify(projectFindings), this.headElements))

  }

  ConvertToCSV(json: string, fields: any): string {

    const Json2csvParser = require('json2csv').parse;
    let options: {
    };
    options = fields;
    const csv = Json2csvParser(JSON.parse(json), options);
    return csv.split(/\[/gm).join(' ').split(/\]/gm).join(' ').split(/"",""/gm).join('\n');
  }


  private getResults(value) {
    this.getProjectScan.getCisScan(this.value).subscribe((data: any) => {
      this.projectFindings = data.findings;
      this.table_name = data.table[0].table_id;
      this.modified_date = data.table[0].last_modified_date;
      this.showSpinner = false;
      this.showTable = true;
    },
      (data) => {
        this.showModal = true;
        this.errors = data;
        this.showSpinner = false;
      });
  }

}
