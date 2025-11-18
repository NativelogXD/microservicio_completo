import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VuelosSave } from './vuelos-save';

describe('VuelosSave', () => {
  let component: VuelosSave;
  let fixture: ComponentFixture<VuelosSave>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VuelosSave]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VuelosSave);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
