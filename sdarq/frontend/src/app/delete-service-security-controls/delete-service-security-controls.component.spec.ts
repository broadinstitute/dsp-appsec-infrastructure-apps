import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeleteServiceSecurityControlsComponent } from './delete-service-security-controls.component';

describe('DeleteServiceSecurityControlsComponent', () => {
  let component: DeleteServiceSecurityControlsComponent;
  let fixture: ComponentFixture<DeleteServiceSecurityControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeleteServiceSecurityControlsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeleteServiceSecurityControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
