import { TestBed } from '@angular/core/testing';

import { ScanServiceService } from './scan-service.service';

describe('ScanServiceService', () => {
  let service: ScanServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ScanServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
