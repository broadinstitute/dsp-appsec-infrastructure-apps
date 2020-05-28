import { Component, OnInit } from '@angular/core';
import { GetCisScanService } from '../services/get-cis-scan.service';
import { ActivatedRoute } from '@angular/router';

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

  headElements = ['Id', 'Level', 'Impact', 'Title', 'Failures', 'Description', 'Rationale', 'Refs'];

  constructor(private getProjectScan: GetCisScanService, private router: ActivatedRoute) { }

  ngOnInit() {
    this.showSpinner = true;
    this.router.queryParams.subscribe(params => {
      this.value = params.project_id
      this.getResults(this.value)
    })
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
