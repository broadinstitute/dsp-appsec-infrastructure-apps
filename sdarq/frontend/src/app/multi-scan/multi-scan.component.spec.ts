import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MultiScanComponent } from './multi-scan.component';

describe('MultiScanComponent', () => {
  let component: MultiScanComponent;
  let fixture: ComponentFixture<MultiScanComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ MultiScanComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(MultiScanComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
