import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeResult } from './code-result';

describe('CodeResult', () => {
  let component: CodeResult;
  let fixture: ComponentFixture<CodeResult>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeResult],
    }).compileComponents();

    fixture = TestBed.createComponent(CodeResult);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
