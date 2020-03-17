import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-mainpage',
  templateUrl: './mainpage.component.html',
  styleUrls: ['./mainpage.component.css']
})
export class MainpageComponent implements OnInit {

  partofDSP = false;
  notPartOfDSP = false;

  constructor() { }

  ngOnInit() {
  }

isPartOfDSP(partOfDSP1) {
    if(partOfDSP1 === true) {
      this.partofDSP = true;
      this.notPartOfDSP = false;
    }
}

isNotPartOfDSP(partOfDSP2) {
    if(partOfDSP2 === true) {
      this.notPartOfDSP = true;
      this.partofDSP = false;
    }
}
}
