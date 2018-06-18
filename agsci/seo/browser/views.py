from BTrees.OOBTree import OOBTree
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.sitemap.sitemap import SiteMapView as _SiteMapView
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import implements, Interface

from Products.agCommon.browser.views import FolderView
from agsci.seo import exclude_types

class ICanonicalRedirectView(Interface):
    pass


class CanonicalRedirectView(FolderView):

    """
    Redirects entity to the corresponding content based on canonical URL
    """

    implements(ICanonicalRedirectView)

    def __call__(self):
        context = self.context
        mtool = getToolByName(context, 'portal_membership')
        can_edit = mtool.checkPermission('Modify portal content', context)

        redirectURL = None

        refs = self.context.getReferences(relationship = 'IsCanonicalURLFor')

        if refs:
            # Just in case it has multiples
            redirectURL = refs[0].absolute_url()

        elif hasattr(context, 'canonical_url_text') and getattr(context, 'canonical_url_text'):
            redirectURL = context.canonical_url_text

        if redirectURL and not can_edit:
            # Send to the configured website
            return context.REQUEST.RESPONSE.redirect(redirectURL)
        else:
            # Render the first layout listed
            layout = 'base_view'

            for (l,t) in context.getAvailableLayouts():
                if l != 'canonical_redirect':
                    layout = l
                    break

            return eval("context.%s()" % layout)


class SiteMapView(_SiteMapView, FolderView):

    def objects(self):

        # Returns the data to create the sitemap.

        catalog = getToolByName(self.context, 'portal_catalog')

        query = {}

        utils = getToolByName(self.context, 'plone_utils')

        query['portal_type'] = list(set(utils.getUserFriendlyTypes()) - set(exclude_types))

        ptool = getToolByName(self, 'portal_properties')

        siteProperties = getattr(ptool, 'site_properties')

        typesUseViewActionInListings = frozenset(
            siteProperties.getProperty('typesUseViewActionInListings', [])
            )

        is_plone_site_root = IPloneSiteRoot.providedBy(self.context)

        if not is_plone_site_root:
            query['path'] = '/'.join(self.context.getPhysicalPath())

        # Query to set modified times for folders with default pages
        # to the modified time for the default page.
        query['is_default_page'] = True

        default_page_modified = OOBTree()

        for item in catalog.searchResults(query, Language='all'):
            key = item.getURL().rsplit('/', 1)[0]
            value = (item.modified.micros(), item.modified.ISO8601())
            default_page_modified[key] = value

        # The plone site root is not catalogued.
        if is_plone_site_root:
            loc = self.context.absolute_url()
            date = self.context.modified()

            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)

            if default_modified is not None:
                modified = max(modified, default_modified)

            lastmod = modified[1]

            yield {
                'loc': loc,
                'lastmod': lastmod,
                #'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
                #'prioriy': 0.5, # 0.0 to 1.0
            }

        # Query for all of the non-default page objects

        now = DateTime()

        query['is_default_page'] = False

        for item in catalog.searchResults(query, Language='all'):
            loc = self.getItemURL(item)
            date = item.modified

            # Comparison must be on GMT value
            modified = (date.micros(), date.ISO8601())
            default_modified = default_page_modified.get(loc, None)

            if default_modified is not None:
                modified = max(modified, default_modified)

            lastmod = modified[1]

            # Don't include finished events
            if item.portal_type in ['Event'] and item.end < now:
                continue

            # Don't include items with exclude_from_robots checked
            if getattr(item, 'exclude_from_robots', True):
                continue

            yield {
                'loc': loc,
                'lastmod': lastmod,
                #'changefreq': 'always', # hourly/daily/weekly/monthly/yearly/never
                #'prioriy': 0.5, # 0.0 to 1.0
            }

class RobotsTxtView(BrowserView):

    registry_key = "agsci.seo.robots"

    @property
    def registry(self):
        return getUtility(IRegistry)

    def getRegistryDisallowedPaths(self):

        value = self.registry.get(self.registry_key)

        if value and isinstance(value, (list, tuple)):
            return list(value)

        return []

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return self.index()

    def getDisallowedPaths(self):

        # Initialize list
        disallow = []
        
        # Add the values we have hardcoded in the registry
        disallow.extend(self.getRegistryDisallowedPaths())
        
        # Query the catalog for items with 'exclude_from_robots' set to True
        portal_catalog = getToolByName(self.context, 'portal_catalog')

        results = [x for x in portal_catalog.searchResults({'exclude_from_robots' : True})]

        portal_url = self.context.portal_url()

        for r in results:
            disallow.append(r.getURL().replace(portal_url, '') )

        return sorted(list(set(disallow)))

