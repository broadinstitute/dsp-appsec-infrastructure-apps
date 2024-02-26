import { Component, OnInit } from '@angular/core';
import { AuthzService } from '../services/authz/authz.service'
import {  map } from 'rxjs/operators';



@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

showMenuItem: boolean;

  constructor(private authzService: AuthzService) {
    // This is intentional
   }

  ngOnInit() {
    console.log(this.showMenuItem)
    this.getResults()
  }

  private getResults(){ this.authzService.fetchUserDetails().pipe(
    map(response => {
      if (response.verified === true) {
        console.log(response.verified)
        this.showMenuItem = true;
      } else {
        console.log(response.verified)
        this.showMenuItem = false;
      }
    }))
}
}
