import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditSecurityControlsFormComponent } from './edit-security-controls-form.component';

describe('EditSecurityControlsFormComponent', () => {
  let component: EditSecurityControlsFormComponent;
  let fixture: ComponentFixture<EditSecurityControlsFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ EditSecurityControlsFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(EditSecurityControlsFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
