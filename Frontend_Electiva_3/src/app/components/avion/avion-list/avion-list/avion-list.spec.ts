import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AvionList } from './avion-list';

describe('AvionList', () => {
  let component: AvionList;
  let fixture: ComponentFixture<AvionList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AvionList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AvionList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
