import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceScanComponent } from './service-scan.component';

describe('ServiceScanComponent', () => {
  let component: ServiceScanComponent;
  let fixture: ComponentFixture<ServiceScanComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceScanComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ServiceScanComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
