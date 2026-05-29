import { TestBed } from '@angular/core/testing';

import { Migration } from './migration';

describe('Migration', () => {
  let service: Migration;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Migration);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
