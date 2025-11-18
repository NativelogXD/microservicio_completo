import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VuelosEdit } from './vuelos-edit';

describe('VuelosEdit', () => {
  let component: VuelosEdit;
  let fixture: ComponentFixture<VuelosEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VuelosEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VuelosEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
