import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CVSSPageComponent } from './cvsspage.component';

describe('CVSSPageComponent', () => {
  let component: CVSSPageComponent;
  let fixture: ComponentFixture<CVSSPageComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [CVSSPageComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CVSSPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
