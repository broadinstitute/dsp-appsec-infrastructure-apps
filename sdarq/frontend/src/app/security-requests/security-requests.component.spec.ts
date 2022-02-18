import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecurityRequestsComponent } from './security-requests.component';

describe('SecurityRequestsComponent', () => {
  let component: SecurityRequestsComponent;
  let fixture: ComponentFixture<SecurityRequestsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SecurityRequestsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SecurityRequestsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
