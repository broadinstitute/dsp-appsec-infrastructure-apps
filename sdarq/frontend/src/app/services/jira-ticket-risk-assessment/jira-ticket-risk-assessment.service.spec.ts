import { TestBed } from '@angular/core/testing';

import { JiraTicketRiskAssessmentService } from './jira-ticket-risk-assessment.service';

describe('JiraTicketRiskAssessmentService', () => {
  let service: JiraTicketRiskAssessmentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(JiraTicketRiskAssessmentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
