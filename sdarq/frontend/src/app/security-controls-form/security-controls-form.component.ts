import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import formJson from './form.json';
import { CreateNewSctService } from '../services/create-new-security-controls/create-new-sct.service';


@Component({
  selector: 'app-security-controls-form',
  templateUrl: './security-controls-form.component.html',
  styleUrls: ['./security-controls-form.component.css']
})
export class SecurityControlsFormComponent implements OnInit {

  showModalErr: boolean = false;
  showForm: boolean = true;
  showModalError: string;

  json = formJson;

  constructor(private createSCT: CreateNewSctService,
              private ngZone: NgZone,
              private ref: ChangeDetectorRef) { }

  ngOnInit(): void {}

  sendSCTData(result) {
    this.createSCT.createNewSCT(result).subscribe(() => {
      this.ref.detectChanges();
    },
      (data) => {    
        this.ngZone.run(() => {
          this.showModalErr = true;
          this.showForm = false;
          this.showModalError = data;
      });    
      });
  }
}

