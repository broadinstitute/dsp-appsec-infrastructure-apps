import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecurityControlsListComponent } from './security-controls-list.component';

describe('SecurityControlsListComponent', () => {
  let component: SecurityControlsListComponent;
  let fixture: ComponentFixture<SecurityControlsListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecurityControlsListComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SecurityControlsListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
