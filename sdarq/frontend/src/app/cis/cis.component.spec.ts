import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CisComponent } from './cis.component';

describe('CisComponent', () => {
  let component: CisComponent;
  let fixture: ComponentFixture<CisComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CisComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CisComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
