import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { AuthzService } from './services/authz/authz.service';
import { map } from 'rxjs/operators';

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
      map(isAuthorized => {
        if (!isAuthorized) {
          this.router.navigate(['/']);
          console.log("false :)");
          return false;
        }
        console.log("true :)");
        return true;
      })
    );
  }
}

