import { Component, OnInit } from '@angular/core';
import { AuthzService } from './services/authz/authz.service';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {
  constructor(private authzService: AuthzService) {}

  ngOnInit() {
    this.authzService.fetchUserDetails().subscribe(details => {
      this.authzService.setUserDetails(details);
      console.log(details)
    });
  }
}
