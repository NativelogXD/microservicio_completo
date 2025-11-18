import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvionSave } from './avion-save';

describe('AvionSave', () => {
  let component: AvionSave;
  let fixture: ComponentFixture<AvionSave>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AvionSave]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvionSave);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
