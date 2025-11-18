import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReservasEdit } from './reservas-edit';

describe('ReservasEdit', () => {
  let component: ReservasEdit;
  let fixture: ComponentFixture<ReservasEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReservasEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReservasEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
