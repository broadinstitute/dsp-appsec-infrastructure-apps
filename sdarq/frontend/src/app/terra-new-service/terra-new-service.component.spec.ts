import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerraNewServiceComponent } from './terra-new-service.component';

describe('TerraNewServiceComponent', () => {
  let component: TerraNewServiceComponent;
  let fixture: ComponentFixture<TerraNewServiceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TerraNewServiceComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TerraNewServiceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
