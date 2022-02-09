import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecurityControlsComponent } from './security-controls.component';

describe('SecurityControlsComponent', () => {
  let component: SecurityControlsComponent;
  let fixture: ComponentFixture<SecurityControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecurityControlsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SecurityControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
