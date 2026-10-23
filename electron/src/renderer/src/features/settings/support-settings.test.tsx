import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

const mock = vi.hoisted(() => ({ open: vi.fn().mockResolvedValue(undefined) }));
vi.mock('@/components/bridge', () => ({
  getBridge: () => ({ files: { openExternal: mock.open } }),
}));
vi.mock('react-i18next', async (importOriginal) => ({
  ...(await importOriginal<typeof import('react-i18next')>()),
  useTranslation: () => ({ t: (key: string) => key }),
}));

import { SupportSettings } from './support-settings';

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

it('opens SpeechNexa project destinations without inherited owner links', () => {
  render(<SupportSettings />);
  expect(screen.getByRole('heading', { name: 'app.name' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'contact.security_cta' })).toHaveAttribute(
    'href',
    'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio/security/advisories/new',
  );
  expect(screen.getByRole('link', { name: 'contact.feature_cta' })).toHaveAttribute(
    'href',
    'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio/issues',
  );
  const repository = screen.getByRole('link', { name: 'support.star_github' });
  fireEvent.click(repository);
  expect(mock.open).toHaveBeenCalledWith(
    'https://github.com/Gaurav598/SpeechNexa-AI-Voice-Studio',
  );
  expect(screen.queryByRole('link', { name: 'GitHub Sponsors' })).not.toBeInTheDocument();
});
