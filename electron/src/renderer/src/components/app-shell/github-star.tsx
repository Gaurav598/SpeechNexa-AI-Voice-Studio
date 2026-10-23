import { useTranslation } from 'react-i18next';
import { StarIcon } from 'lucide-react';
import { getBridge } from '@/components/bridge';
import { runRendererTask } from '@/lib/global-error-recovery';
import { REPO_URL } from '@shared/utils/contactLinks';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip';

/** A repository shortcut without an inherited or speculative star count. */
export function GithubStar() {
  const { t } = useTranslation();
  return (
    <Tooltip>
      <TooltipTrigger
        render={
          <a
            href={REPO_URL}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={t('support.star_github')}
            className="github-star-shortcut app-no-drag inline-flex h-8 shrink-0 items-center gap-1.5 px-2.5 text-xs font-semibold focus-visible:outline-2 focus-visible:outline-ring"
            onClick={(event) => {
              const bridge = getBridge();
              if (!bridge) return;
              event.preventDefault();
              runRendererTask('Open project repository', () => bridge.files.openExternal(REPO_URL));
            }}
          />
        }
      >
        <StarIcon aria-hidden="true" className="size-3.5" />
        <span>{t('support.star_short')}</span>
      </TooltipTrigger>
      <TooltipContent surface="theme" side="bottom">
        {t('support.star_github')}
      </TooltipContent>
    </Tooltip>
  );
}
