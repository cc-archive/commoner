from django.shortcuts import render_to_response
from django.db.models import Avg, Count, Min, Max
from datetime import datetime
from dateutil.relativedelta import relativedelta

from commoner.profiles.models import CommonerProfile
from commoner.works.models import Work, Registration
        
def stats(request):
    
    """ Page displays some simple statistics of the user activity on CC Net"""
    
    # get the earliest date joined and start monthly stats there
    # should be hardcoded since this obviously never changes
    start = CommonerProfile.objects.aggregate(start=Min('user__date_joined'))
    
    def date_range(start, end):
        dates = []
        date = datetime(start.year, start.month, start.day)
        while date < end:
            dates.append(date)
            # not accurate 
            date = date + relativedelta(months=+1)
        return dates
    
    months = date_range(start['start'], datetime.now())

    stats = []
    totals = {'users':0,'works':0}
    
    for i in range(0,len(months)):
        
        month = months[i]        
        
        # count all of the users added for this month
        u = CommonerProfile.objects.filter(
                user__date_joined__gte=month,
                user__date_joined__lt=month+relativedelta(months=+1)
            ).aggregate(num_of_users=Count('nickname'))
        
        # count all of the works added in this month
        w = Work.objects.filter(
                registered__gte=month,
                registered__lt=month+relativedelta(months=+1)
            ).aggregate(num_of_works=Count('title'))
        
        
        # need to make statistics more elegant
        try:
            u_growth = u['num_of_users'] / float(totals['users'])
            w_growth = w['num_of_works'] / float(totals['works'])
        except ZeroDivisionError:
            u_growth = u['num_of_users']
            w_growth = w['num_of_works']
        except IndexError:
            u_growth = 0
            w_growth = 0
        
        totals['users'] += u['num_of_users']
        totals['works'] += w['num_of_works']
            
        stats.append({
            'end_month':month.strftime("%Y-%m"), 
            'users_new':totals['users'],
            'users_growth': int(u_growth * 100),
            'works_new':totals['works'],
            'works_growth': int(w_growth * 100),
        })
        
        
    # flexing the Django aggregation muscles
    """
    works = CommonerProfile.objects.annotate(
                num_works=Count('user__registrations__works')
            ).aggregate(
                mean=Avg('num_works')
            )
    totals['works_avg'] = works['mean']
    """
    
    return render_to_response('metrics/stats.html', {'stats':stats,'totals':totals})