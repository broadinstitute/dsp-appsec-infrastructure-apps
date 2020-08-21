import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { JiraTicketRiskAssesmentComponent } from './jira-ticket-risk-assesment.component';

describe('JiraTicketRiskAssesmentComponent', () => {
  let component: JiraTicketRiskAssesmentComponent;
  let fixture: ComponentFixture<JiraTicketRiskAssesmentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ JiraTicketRiskAssesmentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(JiraTicketRiskAssesmentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
