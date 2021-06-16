import { Component, OnInit } from '@angular/core';
import { GetSecurityControlsService } from '../services/get-security-controls.service'
import { ActivatedRoute } from '@angular/router';
import { ServiceSecurityControl } from '../models/service-security-control.model';


@Component({
  selector: 'app-security-controls-list',
  templateUrl: './security-controls-list.component.html',
  styleUrls: ['./security-controls-list.component.css']
})
export class SecurityControlsListComponent implements OnInit {

   serviceSecurityControl: ServiceSecurityControl[];

  constructor(private getSecurityControls: GetSecurityControlsService, private router: ActivatedRoute ) { }

  ngOnInit() {
    this.router.queryParams.subscribe(params => {
      this.getResults()
    })
  }

  getResults() {
    this.getSecurityControls.getAllSecurityControls().subscribe((serviceSecurityControl) => {
      this.serviceSecurityControl = serviceSecurityControl
    },
      (data) => {
      });
  }

}
