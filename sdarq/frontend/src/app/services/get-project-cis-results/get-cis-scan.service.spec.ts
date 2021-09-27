import { TestBed } from '@angular/core/testing';

import { GetCisScanService } from './get-cis-scan.service';

describe('GetCisScanService', () => {
  let service: GetCisScanService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetCisScanService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
