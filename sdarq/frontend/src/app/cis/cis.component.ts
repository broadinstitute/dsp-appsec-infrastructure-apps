import { Component, OnInit } from '@angular/core';
import { CisProjectService } from '../cis-project.service';
import { HttpClient } from '@angular/common/http';

import { FormBuilder, FormGroup, Validators} from '@angular/forms';

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
  
  projectIdPattern = "^[a-z][a-z0-9-]{4,28}[a-z0-9]$" // pattern


  constructor(private sendProject: CisProjectService, private http: HttpClient, private form: FormBuilder) { 
    this.submitForm = form.group({
     'project_id': this.project_id
      });
  }

  ngOnInit() {
    this.submitForm = this.form.group({
      project_id: ['', [Validators.required, Validators.pattern(this.projectIdPattern), Validators.minLength(6), Validators.maxLength(30)]]
    })
  }

  get f() {
    return this.submitForm.controls;
  }


  submit() {
    if (this.submitForm.invalid) {
      return;
    } else {
    this.sendProject.sendCisProject(this.submitForm.value).subscribe((data:any) => {
      this.projectFindings = data;
      this.table_show = true;
    }),
    (data) => {
      console.log('Form not sent');
     }
}
}
}