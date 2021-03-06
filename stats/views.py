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
    def get_recent_stats(self, most_recent_data):
        age = int((datetime.now(pytz.utc) - convert_datestring_to_dateobj(most_recent_data[0])) / timedelta(minutes=1))
        recent = {
            'data': {
                '1v1m': most_recent_data[1],
                '1v1q': most_recent_data[2],
                'ffam': most_recent_data[3],
                'ffaq': most_recent_data[4]
            },
            'time': {
                'age': age,
                'timestamp': most_recent_data[0]
            }
            
            
        }
        return recent

    def analyze_data(self, since):

        try:
            from_datetime = datetime.strptime(since, '%Y-%m-%d %H:%M:%S')
            from_datetime = from_datetime.replace(tzinfo=pytz.UTC)
        except ValueError:
            return HttpResponse("Couldn't parse time")
        result = {
            '1v1m': [],
            '1v1q': [],
            'ffam': [],
            'ffaq': []
        }
        with open('stats/data/rankedhistory.log', newline='') as f:
            now = datetime.now(pytz.utc)
            data = csv.reader(f)

            for item in data:
                time_raw = item[0]

                #timezone conversion
                time_utc = convert_datestring_to_dateobj(time_raw)

                if(time_utc<from_datetime):
                    continue

                result['1v1m'].append({'time': str(time_utc)[0:-6], 'val': item[1]})
                result['1v1q'].append({'time': str(time_utc)[0:-6], 'val': item[2]})
                result['ffam'].append({'time': str(time_utc)[0:-6], 'val': item[3]})
                result['ffaq'].append({'time': str(time_utc)[0:-6], 'val': item[4]})

            result['recent'] = self.get_recent_stats(item)
            print(result['ffam'][0]['time'])
            return result


    def get(self, request, since="1970-03-02 21:39:40"):
        data = self.analyze_data(since)
        return JsonResponse(data)