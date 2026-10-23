import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

const mock = vi.hoisted(() => ({
  open: vi.fn().mockResolvedValue(undefined),
  navigate: vi.fn(),
}));
vi.mock('@/components/bridge', () => ({
  getBridge: () => ({ files: { openExternal: mock.open } }),
}));
vi.mock('@tanstack/react-router', () => ({ useNavigate: () => mock.navigate }));
vi.mock('react-i18next', () => ({
  useTranslation: () => ({ t: (key: string) => key }),
}));

import { SponsorFooter } from './sponsor-footer';

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

it('keeps integrations and the SpeechNexa repository reachable', async () => {
  render(<SponsorFooter />);
  fireEvent.click(screen.getByRole('button', { name: 'integrationCatalog.title' }));
  expect(mock.navigate).toHaveBeenCalledWith({ to: '/integrations' });
  const repository = screen.getByRole('link', { name: 'support.star_github' });
  expect(repository).toHaveAttribute(
    'href',
    'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio',
  );
  fireEvent.click(repository);
  await waitFor(() =>
    expect(mock.open).toHaveBeenCalledWith(
      'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio',
    ),
  );
  expect(screen.queryByRole('button', { name: 'sponsorSlot.footer_brand' })).toBeNull();
  expect(screen.queryByRole('link', { name: 'support.join_discord' })).toBeNull();
});

it('collapses and restores the footer', () => {
  render(<SponsorFooter />);
  fireEvent.click(screen.getByRole('button', { name: 'homeUi.collapseFooter' }));
  expect(screen.queryByRole('contentinfo')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'homeUi.expandFooter' }));
  expect(screen.getByRole('contentinfo')).toBeVisible();
});
