import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AppQuestionnaireComponent } from './app-questionnaire.component';

describe('AppQuestionnaireComponent', () => {
  let component: AppQuestionnaireComponent;
  let fixture: ComponentFixture<AppQuestionnaireComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AppQuestionnaireComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AppQuestionnaireComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
