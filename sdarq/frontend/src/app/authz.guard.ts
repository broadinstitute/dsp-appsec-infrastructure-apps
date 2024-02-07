import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthzService } from './services/authz/authz.service';
import { map } from 'rxjs/operators';
import { HttpResponse } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthzGuard implements CanActivate {
  constructor(private authzService: AuthzService, private router: Router) {}
  
  statusreturned: boolean;

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return this.authzService.fetchUserDetails().pipe(
      map((response: HttpResponse<any>) => {
        if (response.status === 200) {
          console.log("True")
          return true;
        } else if (response.status === 403) {
          console.log("False")
          this.router.navigate(['/']);
          return false;
        }
      })
    );
  }
}

