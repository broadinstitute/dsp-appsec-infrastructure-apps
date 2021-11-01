import { TestBed } from '@angular/core/testing';

import { RequestTmService } from './request-tm.service';

describe('RequestTmService', () => {
  let service: RequestTmService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(RequestTmService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
