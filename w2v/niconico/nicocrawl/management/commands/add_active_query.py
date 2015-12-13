from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from nicocrawl.models import Query, Queryhistory
from datetime import datetime,timedelta,date

class Command(BaseCommand):
    help = ("runs the niconico snapshot api and stores movie and tag info.")

    requires_system_checks = False
    def add_arguments(self, parser):
        parser.add_argument('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database onto which to '
            'open a shell. Defaults to the "default" database.')

    def handle(self, **options):
        connection = connections[options.get('database')]
        yesterday = date.today() - timedelta(days=1)

        active_queries =  Query.objects.filter(is_active=1)
        for active_query in active_queries:
            queryhistory, created = Queryhistory.objects.get_or_create(
                    query=active_query, date=yesterday,
                    defaults={"query":active_query.query, "date":yesterday, "total":0, "offset":0}
                    )
            if created:
                queryhistory.save()
