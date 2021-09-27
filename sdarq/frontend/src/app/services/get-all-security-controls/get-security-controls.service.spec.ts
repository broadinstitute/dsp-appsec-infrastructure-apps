import { TestBed } from '@angular/core/testing';

import { GetSecurityControlsService } from './get-security-controls.service';

describe('GetSecurityControlsService', () => {
  let service: GetSecurityControlsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetSecurityControlsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
