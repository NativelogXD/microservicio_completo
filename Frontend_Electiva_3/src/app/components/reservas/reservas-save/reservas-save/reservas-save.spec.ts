import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReservasSave } from './reservas-save';

describe('ReservasSave', () => {
  let component: ReservasSave;
  let fixture: ComponentFixture<ReservasSave>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReservasSave]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReservasSave);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
