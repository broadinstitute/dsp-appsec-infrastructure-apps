import { TestBed } from '@angular/core/testing';

import { SendFormDataService } from './send-form-data.service';

describe('SendFormDataService', () => {
  beforeEach(() => TestBed.configureTestingModule({}));

  it('should be created', () => {
    const service: SendFormDataService = TestBed.get(SendFormDataService);
    expect(service).toBeTruthy();
  });
});
