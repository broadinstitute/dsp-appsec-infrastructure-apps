import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ServiceSecurityControlsComponent } from './service-security-controls.component';

describe('ServiceSecurityControlsComponent', () => {
  let component: ServiceSecurityControlsComponent;
  let fixture: ComponentFixture<ServiceSecurityControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ServiceSecurityControlsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ServiceSecurityControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
