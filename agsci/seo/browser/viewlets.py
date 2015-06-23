from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase
from DateTime import DateTime
from agsci.seo import exclude_types

class CanonicalURLViewlet(ViewletBase):

    def show_message(self):
        return (self.canonical_url and not self.anonymous)

    @property
    def anonymous(self):
        return self.portal_state.anonymous()

    @property
    def canonical_url(self):

        # Look up canonical URL refs
        refs = self.context.getReferences(relationship = 'IsCanonicalURLFor')

        if refs:
            # Just in case it has multiples
            return refs[0].absolute_url()
        else:
            # Look for the string field
            return getattr(self.context, 'canonical_url_text', '')

    



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
