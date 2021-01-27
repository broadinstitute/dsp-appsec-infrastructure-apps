import { TestBed } from '@angular/core/testing';

import { CsvDataService } from './csv-data.service';

describe('CsvDataService', () => {
  let service: CsvDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CsvDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
