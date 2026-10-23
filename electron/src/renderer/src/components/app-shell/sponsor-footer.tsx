import { useState } from 'react';
import { useNavigate } from '@tanstack/react-router';
import { BlocksIcon, ChevronDownIcon, ChevronUpIcon, StarIcon } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { getBridge } from '@/components/bridge';
import { runRendererTask } from '@/lib/global-error-recovery';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { REPO_URL } from '@shared/utils/contactLinks';
import './sponsor-footer.css';

/** Project links live below the content without covering the editor. */
export function SponsorFooter() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState(false);

  if (collapsed)
    return (
      <div className="flex h-6 shrink-0 justify-end border-t border-border/50 bg-sidebar px-2">
        <button
          type="button"
          aria-label={t('homeUi.expandFooter')}
          title={t('homeUi.expandFooter')}
          aria-expanded={false}
          onClick={() => setCollapsed(false)}
          className="flex w-8 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-foreground focus-visible:outline-2 focus-visible:outline-ring"
        >
          <ChevronUpIcon className="size-3.5" aria-hidden="true" />
        </button>
      </div>
    );

  return (
    <div className="sponsor-footer-host">
      <footer aria-label={t('integrationCatalog.title')} className="sponsor-strip">
        <button
          type="button"
          className="sponsor-footer-action"
          onClick={() =>
            runRendererTask('Open integrations', () => navigate({ to: '/integrations' }))
          }
        >
          <BlocksIcon aria-hidden="true" className="size-4" />
          <span>{t('integrationCatalog.title')}</span>
        </button>
        <div className="sponsor-footer-links">
          <Tooltip>
            <TooltipTrigger
              render={
                <a
                  href={REPO_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="sponsor-footer-pro"
                  aria-label={t('support.star_github')}
                  onClick={(event) => {
                    const bridge = getBridge();
                    if (!bridge) return;
                    event.preventDefault();
                    runRendererTask('Open project repository', () => bridge.files.openExternal(REPO_URL));
                  }}
                />
              }
            >
              <StarIcon aria-hidden="true" className="size-4" />
            </TooltipTrigger>
            <TooltipContent surface="theme" side="top">
              {t('support.star_github')}
            </TooltipContent>
          </Tooltip>
          <Tooltip>
            <TooltipTrigger
              render={
                <button
                  type="button"
                  className="sponsor-footer-pro"
                  aria-label={t('homeUi.collapseFooter')}
                  aria-expanded={true}
                  onClick={() => setCollapsed(true)}
                />
              }
            >
              <ChevronDownIcon aria-hidden="true" className="size-4" />
            </TooltipTrigger>
            <TooltipContent surface="theme" side="top">
              {t('homeUi.collapseFooter')}
            </TooltipContent>
          </Tooltip>
        </div>
      </footer>
    </div>
  );
}
