import { TestBed } from '@angular/core/testing';

import { GetServiceSecurityControlsService } from './get-service-security-controls.service';

describe('GetServiceSecurityControlsService', () => {
  let service: GetServiceSecurityControlsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetServiceSecurityControlsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
