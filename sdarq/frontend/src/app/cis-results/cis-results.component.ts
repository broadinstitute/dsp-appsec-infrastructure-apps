import { Component, OnInit } from '@angular/core';
import { GetCisScanService } from '../services/get-project-cis-results/get-cis-scan.service';
import { ActivatedRoute } from '@angular/router';
import { CsvDataService } from '../services/convert-json-to-csv/csv-data.service';

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
  errors: string;
  showTable: boolean;
  filename: string;
  projectId: string;
  updateDate: Date;
  headElements = ['Benchmark', 'Id', 'Level', 'CVSS', 'Title', 'Failures', 'Description', 'Rationale', 'Refs'];


  constructor(private getProjectScan: GetCisScanService, private router: ActivatedRoute, private csvService: CsvDataService) { }

  ngOnInit() {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.project_id
      this.getResults(this.value)
    })
  }

  saveAsCSV(projectFindings, updateDate, projectId) {
    this.filename = ['GCP_CIS_Results_', projectId, '_', updateDate.toISOString(), '.csv'].join('');
    const csvContent = this.csvService.ConvertToCSV(JSON.stringify(projectFindings), this.headElements);
    this.csvService.exportToCsv(this.filename, csvContent);
  }

  private getResults(value) {
    this.getProjectScan.getCisScan(this.value).subscribe((data) => {
      this.projectFindings = data.findings;
      this.projectId = data.meta.projectId;
      this.updateDate = new Date(data.meta.lastModifiedDatetime);
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
