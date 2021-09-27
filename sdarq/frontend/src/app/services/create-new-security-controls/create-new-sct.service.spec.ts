import { TestBed } from '@angular/core/testing';

import { CreateNewSctService } from './create-new-sct.service';

describe('CreateNewSctService', () => {
  let service: CreateNewSctService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CreateNewSctService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
