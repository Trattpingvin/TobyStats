from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views import View
import csv
from datetime import datetime, date, timedelta
import pytz
from collections import defaultdict

# Create your views here.
def convert_datestring_to_dateobj(datestring):
    return datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz.utc)


class IndexView(View):
    def get(self, request):
        return render(request, 'stats/main.html', {})


class ChartView(View):
    def is_recent(self, date, now, day_range):
        delta = (now - date).days
        if delta >= 0 and delta < day_range:
            return True
        return False

    def add_list_items(self, list_storage, list_add_value):
        assert(len(list_storage) == len(list_add_value))
        for idx, value in enumerate(list_add_value):
            list_storage[idx] += int(value)

    def get_recent_stats(self, most_recent_data):
        age = int((datetime.now(pytz.utc) - convert_datestring_to_dateobj(most_recent_data[0])) / timedelta(minutes=1))
        recent = {
            'age': age,
            '1v1m': most_recent_data[1],
            '1v1q': most_recent_data[2],
            'FFAm': most_recent_data[3],
            'FFAq': most_recent_data[4]
        }
        return recent


    def analyze_data(self, mode, days, tz):
        if mode == 'all': get_all = True
        else: get_all = False

        result = {
            '1v1m': [],
            '1v1q': [],
            'ffam': [],
            'ffaq': [],
            'time': {'FFA': [0]*24, '1v1': [0]*24},
            'freq': {'FFA': [0]*7,  '1v1': [0]*7 }
        }
        #{'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0}

        """collect = {
            'time': defaultdict(lambda: defaultdict(int)),
            'freq': defaultdict(lambda: defaultdict(int))
        }"""

        #open file
        with open('stats/data/rankedhistory.log', newline='') as f:
            now = datetime.now(pytz.utc)
            data = csv.reader(f)

            #per line in log, evaluate its time and determine how recent it is
            for item in data:
                local_zone = pytz.timezone(tz)
                time_raw = item[0]

                #timezone conversion
                time_utc = convert_datestring_to_dateobj(time_raw)
                time_loc = time_utc.astimezone(tz=local_zone)

                loc_day = time_loc.weekday()
                loc_hour = time_loc.hour
                #loc_date = time_loc.day

                #generate dict_item
                #FIXME use local time
                dict_1v1m = {'t': time_raw, 'y': item[1]}
                dict_1v1q = {'t': time_raw, 'y': item[2]}
                dict_ffam = {'t': time_raw, 'y': item[3]}
                dict_ffaq = {'t': time_raw, 'y': item[4]}

                #add them to dict
                if get_all or self.is_recent(time_utc, now=now, day_range=days):
                    result['1v1m'].append(dict_1v1m)
                    result['1v1q'].append(dict_1v1q)
                    result['ffam'].append(dict_ffam)
                    result['ffaq'].append(dict_ffaq)
                    #FIXME need to do time aware averaging
                    result['time']['1v1'][loc_hour] += int(item[1])
                    result['time']['FFA'][loc_hour] += int(item[3])
                    result['freq']['1v1'][loc_day] += int(item[1])
                    result['freq']['FFA'][loc_day] += int(item[3])
                else:
                    print('nothing')

            result['recent'] = self.get_recent_stats(item)
            return result


    def get(self, request, mode='all', days=30, tz='UTC'):
        data = self.analyze_data(mode, days, tz)
        return JsonResponse(data)