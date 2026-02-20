import { describe, it, expect } from 'vitest';
import { softmax, scoreFromFeatures } from '../src/score';

describe('softmax', () => {
  it('sums to 1', () => {
    const p = softmax([1, 2, 3]);
    expect(Math.round(p.reduce((a, b) => a + b, 0) * 1000) / 1000).toBe(1);
  });
});

describe('score', () => {
  it('returns top3', () => {
    const res = scoreFromFeatures([0.2, 0.1, 0.3, 0.4, 0.1, 0.2, 0.1, 0.3]);
    expect(res.length).toBe(3);
    expect(res[0].p).toBeGreaterThanOrEqual(res[1].p);
  });
});
