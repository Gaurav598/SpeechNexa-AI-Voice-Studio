import { LightbulbIcon, ShieldCheckIcon, StarIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { brandIcon } from '@/lib/brand';
import { ReportBug } from '@/components/report-bug';
import { ExternalLink } from '@/components/external-link';
import { ISSUES_URL, REPO_URL, SECURITY_URL } from '@shared/utils/contactLinks';
import './support-settings.css';

export function SupportSettings() {
  const { t } = useTranslation();
  const channels = [
    ['contact.feature_cta', ISSUES_URL, LightbulbIcon],
    ['contact.security_cta', SECURITY_URL, ShieldCheckIcon],
    ['support.star_github', REPO_URL, StarIcon],
  ] as const;

  return (
    <div className="support-studio">
      <header className="support-intro">
        <div className="support-emblem" aria-hidden="true">
          <img src={brandIcon} alt="" width={100} height={100} />
        </div>
        <h1>{t('app.name')}</h1>
        <p>{t('app.tagline')}</p>
      </header>
      <section className="support-contact" aria-labelledby="support-contact-heading">
        <div className="support-contact-heading">
          <h2 id="support-contact-heading">{t('contact.channels_label')}</h2>
          <ReportBug />
        </div>
        <div className="support-channel-grid">
          {channels.map(([label, href, Icon]) => (
            <ExternalLink key={href} href={href}>
              <Icon aria-hidden="true" />
              <span>{t(label)}</span>
            </ExternalLink>
          ))}
        </div>
      </section>
    </div>
  );
}
