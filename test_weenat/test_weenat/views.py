from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from test_weenat.models import DataRecord, Measurement, Location, Datalogger
import json


class IngestView(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        try:
            data = json.loads(request.body)

            datalogger, _ = Datalogger.objects.get_or_create(id=data['datalogger'])

            location = Location.objects.create(lat=data['location']['lat'], lng=data['location']['lng'])

            measurements = []
            for m in data['measurements']:
                if m['label'] == "temp" and (m['value'] < -20  or m['value'] > 40):
                    return JsonResponse({"error": "temp is out of range"}, status=400)
                if m['label'] == "hum" and (m['value'] < 20  or m['value'] > 100):
                    return JsonResponse({"error": "hum is out of range"}, status=400)
                if m['label'] == "rain" and (m['value'] < 0  or m['value'] > 2):
                    return JsonResponse({"error": "rain is out of range"}, status=400)


                measurement = Measurement.objects.create(label=m['label'], value=m['value'])
                measurements.append(measurement)

            record = DataRecord.objects.create(at=parse_datetime(data['at']), datalogger=datalogger, location=location)
            record.measurements.set(measurements)

            return JsonResponse({"message": "Record is inserted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


def get_raw_data(since, before, datalogger_id):
    queryset = DataRecord.objects.filter(datalogger__id=datalogger_id)

    if since:
        queryset = queryset.filter(at__gte=parse_datetime(since))
    if before:
        queryset = queryset.filter(at__lte=parse_datetime(before))

    data = []
    for record in queryset:
        for measurement in record.measurements.all():
            data.append({
                "label": measurement.label,
                "measured_at": record.at,
                "value": measurement.value,
            })
    return data

def get_aggregate_data(since, before, span, datalogger_id):
    queryset = DataRecord.objects.filter(datalogger__id=datalogger_id)

    if since:
        queryset = queryset.filter(at__gte=parse_datetime(since))
    if before:
        queryset = queryset.filter(at__lte=parse_datetime(before))

    aggregates = {}
    for record in queryset:
        for measurement in record.measurements.all():
            if span == 'day':
                time_slot = record.at.replace(hour=0, minute=0, second=0, microsecond=0)
            elif span == 'hour':
                time_slot = record.at.replace(minute=0, second=0, microsecond=0)
            else:
                continue

            key = (measurement.label, time_slot)
            if key not in aggregates:
                aggregates[key] = []
            aggregates[key].append(measurement.value)

    data = []
    for (label, time_slot), values in aggregates.items():
        if label == 'rain':
            value = sum(values)
        else:
            value = sum(values) / len(values)
        data.append({
            "label": label,
            "time_slot": time_slot,
            "value": value,
        })
    return data

class DataView(View):
    def get(self, request):
        try:
            since = request.GET.get('since')
            before = request.GET.get('before', None)
            datalogger_id = request.GET.get('datalogger')

            if not datalogger_id:
                return JsonResponse({"error": "Missing required values."}, status=400)

            data = get_raw_data(since, before, datalogger_id)

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

class SummaryView(View):
    def get(self, request):
        try:
            since = request.GET.get('since')
            before = request.GET.get('before', None)
            span = request.GET.get('span', None)
            datalogger_id = request.GET.get('datalogger')

            if not datalogger_id:
                return JsonResponse({"error": "Missing required values."}, status=400)

            if span not in ['hour', 'day']:
                data = get_raw_data(since, before, datalogger_id)
            else:
                data = get_aggregate_data(since, before, span, datalogger_id)

            return JsonResponse(data, safe=False)


        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
