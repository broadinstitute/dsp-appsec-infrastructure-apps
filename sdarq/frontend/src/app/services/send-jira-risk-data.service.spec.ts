import { TestBed } from '@angular/core/testing';

import { SendJiraRiskDataService } from './send-jira-risk-data.service';

describe('SendJiraRiskDataService', () => {
  let service: SendJiraRiskDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SendJiraRiskDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
