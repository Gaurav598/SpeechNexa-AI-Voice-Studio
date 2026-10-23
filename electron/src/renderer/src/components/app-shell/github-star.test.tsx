import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

vi.mock('@/components/bridge', () => ({ getBridge: () => null }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: (key: string) => key }) }));

import { GithubStar } from './github-star';

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

it('links to SpeechNexa without showing or fetching an inherited star count', () => {
  const fetchCount = vi.fn();
  vi.stubGlobal('fetch', fetchCount);
  render(<GithubStar />);
  expect(screen.getByRole('link', { name: 'support.star_github' })).toHaveAttribute(
    'href',
    'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio',
  );
  expect(screen.queryByText('43,638')).not.toBeInTheDocument();
  expect(fetchCount).not.toHaveBeenCalled();
});
