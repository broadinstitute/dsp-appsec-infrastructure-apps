import { ChangeDetectorRef, Component, OnInit } from '@angular/core';
import formJson from './form.json';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';


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

  constructor(private createSCT: CreateNewSctService, private cdRef: ChangeDetectorRef) { }

  ngOnInit() {
    this.showForm = true;
  }

  sendSCTData(result) {
    this.createSCT.createNewSCT(result).subscribe((data) => {
      this.showModalErr = false;
      this.showForm = true;
    },
      (data) => {
        this.cdRef.detectChanges();
        this.showForm = false;
        this.showModalErr = true;
        this.showModalError = data;
      });
  }
}

