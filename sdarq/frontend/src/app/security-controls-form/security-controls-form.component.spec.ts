import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecurityControlsFormComponent } from './security-controls-form.component';

describe('SecurityControlsFormComponent', () => {
  let component: SecurityControlsFormComponent;
  let fixture: ComponentFixture<SecurityControlsFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecurityControlsFormComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SecurityControlsFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
