import { TestBed } from '@angular/core/testing';

import { SendAppFormDataService } from './send-app-form-data.service';

describe('SendAppFormDataService', () => {
  let service: SendAppFormDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SendAppFormDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
