import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchServiceSecurityControlsComponent } from './search-service-security-controls.component';

describe('SearchServiceSecurityControlsComponent', () => {
  let component: SearchServiceSecurityControlsComponent;
  let fixture: ComponentFixture<SearchServiceSecurityControlsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SearchServiceSecurityControlsComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchServiceSecurityControlsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
