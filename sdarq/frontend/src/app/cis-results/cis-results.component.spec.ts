import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CisResultsComponent } from './cis-results.component';

describe('CisResultsComponent', () => {
  let component: CisResultsComponent;
  let fixture: ComponentFixture<CisResultsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CisResultsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CisResultsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
