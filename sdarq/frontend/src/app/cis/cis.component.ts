import { Component, OnInit } from '@angular/core';
import { CisProjectService } from '../cis-project.service';
import { HttpClient } from '@angular/common/http';
import formJson from './form.json';

@Component({
  selector: 'app-cis',
  templateUrl: './cis.component.html',
  styleUrls: ['./cis.component.css']
})
export class CisComponent implements OnInit {
  constructor(private sendProject: CisProjectService, private http: HttpClient) { }


  ngOnInit() {}

  json = formJson

  sendProjectId(result) {
      this.sendProject.sendCisProject(result).subscribe((res) => {
          console.log('Form sent');
        },
        (res) => {
        });
    }
}
