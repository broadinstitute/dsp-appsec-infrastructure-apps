import { TestBed } from '@angular/core/testing';

import { DeleteServiceSecurityControlsService } from './delete-service-security-controls.service';

describe('DeleteServiceSecurityControlsService', () => {
  let service: DeleteServiceSecurityControlsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DeleteServiceSecurityControlsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
