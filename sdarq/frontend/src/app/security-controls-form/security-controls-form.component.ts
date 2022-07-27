import { Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';
import { tick } from '@angular/core/testing';


@Component({
  selector: 'app-security-controls-form',
  templateUrl: './security-controls-form.component.html',
  styleUrls: ['./security-controls-form.component.css']
})
export class SecurityControlsFormComponent implements OnInit {

  showModalErr: boolean;
  showForm: boolean;
  showModalError: string;

  json = formJson;

  constructor(private createSCT: CreateNewSctService) { }

  ngOnInit(): void {
    this.showModalErr = false;
    this.showForm = true;
  }

  sendSCTData(result) {
    this.createSCT.createNewSCT(result).subscribe((data) => {
      this.showModalErr = false;
      this.showForm = true;
    },
      (data) => {
        this.showModalErr = true;
        this.showModalError = data;
        this.showForm = false;
      });
  }
}

