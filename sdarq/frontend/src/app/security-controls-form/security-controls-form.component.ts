import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';


@Component({
  selector: 'app-security-controls-form',
  templateUrl: './security-controls-form.component.html',
  styleUrls: ['./security-controls-form.component.css']
})
export class SecurityControlsFormComponent implements OnInit {

  json = formJson;

  constructor(private createSCT: CreateNewSctService) { }

  ngOnInit(): void {
  }

  sendSCTData(result) {
    this.createSCT.createNewSCT(result).subscribe((data: any) => {
    },
      (data) => {
      });
  }
}

