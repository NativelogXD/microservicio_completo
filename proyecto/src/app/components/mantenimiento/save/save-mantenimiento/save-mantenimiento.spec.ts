import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SaveMantenimiento } from './save-mantenimiento';

describe('SaveMantenimiento', () => {
  let component: SaveMantenimiento;
  let fixture: ComponentFixture<SaveMantenimiento>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SaveMantenimiento]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SaveMantenimiento);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
