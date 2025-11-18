import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvionEdit } from './avion-edit';

describe('AvionEdit', () => {
  let component: AvionEdit;
  let fixture: ComponentFixture<AvionEdit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AvionEdit]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvionEdit);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
