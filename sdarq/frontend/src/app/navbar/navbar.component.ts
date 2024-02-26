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

  ngOnInit(): void {
    this.showMenuItem = false;
    this.getResults()
  }

  private getResults(){ this.authzService.fetchUserDetails().pipe(
    map(response => {
      if (response.verified === true) {
        this.showMenuItem = true;
      } else {
        this.showMenuItem = false;
      }
    }))
}
}
