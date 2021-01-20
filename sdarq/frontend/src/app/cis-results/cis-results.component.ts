import { Component, OnInit } from '@angular/core';
import { GetCisScanService } from '../services/get-cis-scan.service';
import { ActivatedRoute } from '@angular/router';
import { CsvDataService } from '../services/csv-data.service'

@Component({
  selector: 'app-cis-results',
  templateUrl: './cis-results.component.html',
  styleUrls: ['./cis-results.component.css']
})
export class CisResultsComponent implements OnInit {


  result: any;
  projectFindings: any[];
  data: any[];
  params: any;
  value: string;
  showModal: boolean;
  showSpinner: boolean;
  errors: any[];
  showTable: boolean;

  headElements = ['Id', 'Level', 'CVSS', 'Title', 'Failures', 'Description', 'Rationale', 'Refs'];

  constructor(private getProjectScan: GetCisScanService, private router: ActivatedRoute, private csvService: CsvDataService ) { }

  ngOnInit() {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.project_id
      this.getResults(this.value)
    })
  }

  saveAsCSV(projectFindings) {
    this.csvService.exportToCsv('cis-finding.csv', this.projectFindings);
  }


  private getResults(value) {
    this.getProjectScan.getCisScan(this.value).subscribe((data: any) => {
      this.projectFindings = data;
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
