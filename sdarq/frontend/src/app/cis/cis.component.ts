import { Component, OnInit } from '@angular/core';
import { CisProjectService } from '../cis-project.service';
import { HttpClient } from '@angular/common/http';
import { projectFindings } from '../_models/projectFindings';

import { FormBuilder, FormGroup} from '@angular/forms';
import { mapTo } from 'rxjs/operators';

@Component({
  selector: 'app-cis',
  templateUrl: './cis.component.html',
  styleUrls: ['./cis.component.css']
})
export class CisComponent implements OnInit {

  projectFindings: any[];
  data: any[] = [];
  submitForm: FormGroup;
  project_id: FormGroup;
  table_show: boolean = false;
 

  ngOnInit() {}

  constructor(private sendProject: CisProjectService, private http: HttpClient, private form: FormBuilder) { 
    this.submitForm = form.group({
     'project_id': this.project_id
      });
  }

  submit() {
    this.sendProject.sendCisProject(this.submitForm.value).subscribe((data:any) => {
      this.projectFindings = data;
      this.table_show = true;
    }),
    (data) => {
      console.log('Form not sent');
     }
}
}

    

