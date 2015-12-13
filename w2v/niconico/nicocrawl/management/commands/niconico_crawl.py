# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS, connections
from nicocrawl.models import Movie, Tag, Query, Queryhistory
from nicocrawl.snapshot import NicoSnapshot
from datetime import datetime,timedelta

class Command(BaseCommand):
    help = ("runs the niconico snapshot api and stores movie and tag info.")

    requires_system_checks = False
    def add_arguments(self, parser):
        parser.add_argument('--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS, help='Nominates a database onto which to '
            'open a shell. Defaults to the "default" database.')

    def handle(self, **options):
        connection = connections[options.get('database')]
        # 今回の実行対象の情報を nicocrawl_queryhistory から取得
        try :
            target_history = Queryhistory.objects.filter(is_finished=0)[0] #.order_by("id")[0]
        except IndexError:
            return
        target_date = target_history.date
        year = target_date.year
        month = target_date.month
        day = target_date.day
        date_from = "%04d-%02d-%02d 00:00:00" % (year, month, day)
        date_to   = "%04d-%02d-%02d 23:59:59" % (year, month, day)
        # クエリを保存
        querymodel, created = Query.objects.get_or_create(query=target_history.query)
        querymodel.save()
        # set api parameters
        api = NicoSnapshot()
        api.search= ["title","tags"]
        api.join  = [
                "cmsid", "title", "description",
                "tags", "start_time", "thumbnail_url"
                ]
        api.size  = 100
        api.sort_by="start_time"
        api._from   = target_history.offset
        api.query = target_history.query
        api.filters = [{
            "type" : "range", "field" : "start_time", 
            "from" : date_from, "to" : date_to
            }]
        # store api response
        results, status = api.searchAPI()
        if results and results["total"] > 0:
            for movie in results["hits"]:
                t    = datetime.strptime(movie["start_time"]+"+0900","%Y-%m-%d %H:%M:%S%z")
                movie["start_time"] = t
                tags = movie["tags"].split(" ")
                try:
                    moviemodel = Movie.objects.get(id=movie["cmsid"])
                    moviemodel.queries.add(querymodel)
                    moviemodel.save()
                    continue
                except Movie.DoesNotExist:
                    moviemodel = Movie.objects.create(id=movie["cmsid"],
                            title=movie['title'], description=movie['description'],
                            start_time=movie['start_time'], thumbnail_url=movie['thumbnail_url'])
                    for tag in tags:
                        tagmodel,created = Tag.objects.get_or_create(tagname=tag)
                        tagmodel.save()
                        moviemodel.tags.add(tagmodel)
                    moviemodel.queries.add(querymodel)
                    moviemodel.save()

        target_history.offset = api._from
        target_history.total = results["total"]
        if target_history.offset + 100 > target_history.total :
            target_history.is_finished = 1
        else :
            target_history.offset += 100
        target_history.save()

