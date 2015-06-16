from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase
from DateTime import DateTime
from agsci.seo import exclude_types

class CanonicalURLViewlet(ViewletBase):

    def update(self):

        self.canonical_url = ''

        # Look up canonical URL refs
        refs = self.context.getReferences(relationship = 'IsCanonicalURLFor')

        if refs:
            # Just in case it has multiples
            self.canonical_url = refs[0].absolute_url()
        else:
            # Look for the string field
            try:
                if self.context.canonical_url_text:
                    self.canonical_url = self.context.canonical_url_text
            except AttributeError:
                pass


class RobotsMetaViewlet(ViewletBase):

    @property
    def norobots(self):

        now = DateTime()
        
        # Explicit Exclude from Robots checked
        if getattr(self.context, 'exclude_from_robots', False):
            return True

        # Type excluded from search engines
        elif self.context.portal_type in exclude_types:
            return True

        # Event is over

        elif self.context.portal_type in ['Event'] and self.context.end() < now:
            return True

        # Content is expired

        elif self.context.expires() < now:
            return True

        else:
            return False
