import { TestBed } from '@angular/core/testing';

import { CisProjectService } from './cis-project.service';

describe('CisProjectService', () => {
  let service: CisProjectService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CisProjectService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
