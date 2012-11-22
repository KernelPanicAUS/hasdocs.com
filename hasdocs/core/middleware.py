from django.conf import settings
from django.http import Http404

from hasdocs.projects.models import Domain, Project

class SubdomainMiddleware:
    """Middleware for handling subdomains."""
    def process_request(self, request):
        print request
        host = request.get_host()
        subdomain = host.split('.')[0]
        request.slug = None
        if subdomain == 'www':
            request.subdomain = None
        else:
            request.subdomain = subdomain
            request.urlconf = settings.SUBDOMAIN_URLCONF
        # Handle custom domains
        if 'test.com' not in host:
            try:
                # WTF redis or similar for cname lookup may speed up things
                domain = Domain.objects.get(name=host)
                project = Project.objects.get(custom_domains=domain)
                # WTF this part is somewhat ghetto, need to clean up
                request.subdomain = project.owner
                request.slug = project
                request.urlconf = settings.SUBDOMAIN_URLCONF
            except Domain.DoesNotExist:
                # Then CNAME points to our domain, but no record on our side
                raise Http404