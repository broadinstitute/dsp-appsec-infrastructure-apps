import { TestBed } from '@angular/core/testing';

import { EditSecurityControlsService } from './edit-security-controls.service';

describe('EditSecurityControlsService', () => {
  let service: EditSecurityControlsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EditSecurityControlsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
