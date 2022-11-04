import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AppsMainpageComponent } from './apps-mainpage.component';

describe('AppsMainpageComponent', () => {
  let component: AppsMainpageComponent;
  let fixture: ComponentFixture<AppsMainpageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AppsMainpageComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AppsMainpageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
