import { ChangeDetectorRef, Component, NgZone, OnInit } from '@angular/core';
import { DeleteServiceSecurityControlsService } from 'app/services/delete-service-security-controls/delete-service-security-controls.service';
import formJson from './form.json';

@Component({
  selector: 'app-delete-service-security-controls',
  templateUrl: './delete-service-security-controls.component.html',
  styleUrls: ['./delete-service-security-controls.component.css']
})
export class DeleteServiceSecurityControlsComponent implements OnInit {

  showModalErr: boolean;
  showForm: boolean;
  json = formJson;
  error_message: string;

  constructor(private DeleteServiceSecurityControls: DeleteServiceSecurityControlsService,
    private ref: ChangeDetectorRef,
    private ngZone: NgZone) { 
      // This is intentional
    }

  ngOnInit(): void {
    this.showForm = true;
  }

  sendData(result) {
    this.DeleteServiceSecurityControls.removeSecurityControls(result).subscribe(() => {
      this.ref.detectChanges();
    },
      (data) => {
        this.ngZone.run(() => {
        this.showModalErr = true;
        this.showForm = false;
        this.error_message = data;
      });
    });

}
}
