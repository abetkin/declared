from datetime import date, timedelta
from app.filters import qand, qor, CascadeFilter, afilter
from django.db.models import Q

from app.models import Question

class most_recent(CascadeFilter):

    class Filter(qand):
        text = Q(question_text__icontains='where')

        day_ago = date.today() - timedelta(days=2)
        pub_date = Q(pub_date__gt=day_ago)

    @afilter
    def order(qs):
        return qs.order_by('-pub_date')

    @afilter
    def take_two(qs):
        if qs.exists():
            return qs[:2]
        return qs

import ipdb

with ipdb.launch_ipdb_on_exception():
    # ipdb.set_trace()
    mr = most_recent.process_declared(
            Question.objects.all())
    
    print(mr)
