import { TestBed } from '@angular/core/testing';

import { ResponseFormatService } from './response-format-service';

describe('ResponseFormatService', () => {
  let service: ResponseFormatService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ResponseFormatService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
