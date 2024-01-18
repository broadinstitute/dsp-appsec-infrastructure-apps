import { TestBed } from '@angular/core/testing';

import { AuthzGuard } from './authz.guard';

describe('AuthzGuard', () => {
  let guard: AuthzGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    guard = TestBed.inject(AuthzGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });
});
