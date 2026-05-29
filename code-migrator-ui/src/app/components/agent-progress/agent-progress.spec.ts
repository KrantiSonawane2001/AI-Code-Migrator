import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AgentProgress } from './agent-progress';

describe('AgentProgress', () => {
  let component: AgentProgress;
  let fixture: ComponentFixture<AgentProgress>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AgentProgress],
    }).compileComponents();

    fixture = TestBed.createComponent(AgentProgress);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
