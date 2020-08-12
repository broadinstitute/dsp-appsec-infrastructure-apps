import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-cvsspage',
  templateUrl: './cvsspage.component.html',
  styleUrls: ['./cvsspage.component.css']
})
export class CVSSPageComponent implements OnInit {
  c: CVSS

  ngOnInit(): void {
    this.c = new CVSS('cvssboard');
  }
}
