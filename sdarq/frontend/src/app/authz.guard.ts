import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { AuthzService } from './services/authz/authz.service'

@Injectable({
  providedIn: 'root'
})
export class AuthzGuard implements CanActivate {

  constructor(private authzService: AuthzService, private router: Router) {}

  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean> | Promise<boolean> | boolean {
    return this.authzService.fetchUserDetails().pipe(
      map(response => {
        if (response.status === 200) {
          return true;
        } else {
          this.router.navigate(['/']); 
          return false;
        }
      }),
      catchError((error) => {
        if (error.status === 403) {
          this.router.navigate(['/']);
        }
        return of(false);
      })
    );
  }
}