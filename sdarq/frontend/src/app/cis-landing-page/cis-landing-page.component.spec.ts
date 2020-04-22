import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CisLandingPageComponent } from './cis-landing-page.component';

describe('CisLandingPageComponent', () => {
  let component: CisLandingPageComponent;
  let fixture: ComponentFixture<CisLandingPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CisLandingPageComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CisLandingPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
