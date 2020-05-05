import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CisScanComponent } from './cis-scan.component';

describe('CisScanComponent', () => {
  let component: CisScanComponent;
  let fixture: ComponentFixture<CisScanComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CisScanComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CisScanComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
