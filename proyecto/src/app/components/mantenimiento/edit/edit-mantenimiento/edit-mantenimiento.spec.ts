import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditMantenimiento } from './edit-mantenimiento';

describe('EditMantenimiento', () => {
  let component: EditMantenimiento;
  let fixture: ComponentFixture<EditMantenimiento>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditMantenimiento]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EditMantenimiento);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
