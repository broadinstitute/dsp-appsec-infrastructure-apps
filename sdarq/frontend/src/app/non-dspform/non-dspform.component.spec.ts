import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { NonDSPformComponent } from './non-dspform.component';

describe('NonDSPformComponent', () => {
  let component: NonDSPformComponent;
  let fixture: ComponentFixture<NonDSPformComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ NonDSPformComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(NonDSPformComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
