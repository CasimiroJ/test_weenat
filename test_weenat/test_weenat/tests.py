import json
from django.urls import reverse
from django.test import TestCase
from .models import DataRecord, Datalogger, Location, Measurement
from django.utils.dateparse import parse_datetime

class IngestViewTests(TestCase):

    def setUp(self):
        self.url = reverse('ingest')
        self.location_data = {"lat": 47.56321, "lng": 1.524568}
        self.measurements_data = [
            {"label": "temp", "value": 10.52},
            {"label": "rain", "value": 0.0},
        ]
        self.valid_data = {
            'at': "2021-01-02T05:46:22Z",
            'datalogger': "c2a61e2e-068d-4670-a97c-72bfa5e2a58a",
            'location': self.location_data,
            'measurements': self.measurements_data,
        }

    def test_successful_post(self):
        response = self.client.post(self.url, json.dumps(self.valid_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['message'], "Record is inserted successfully")
        self.assertEqual(DataRecord.objects.count(), 1)

    def test_temp_out_of_range(self):
        data = self.valid_data.copy()
        data['measurements'][0]['value'] = -25
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "temp is out of range")

    def test_hum_out_of_range(self):
        data = self.valid_data.copy()
        data['measurements'][1]['label'] = 'hum'
        data['measurements'][1]['value'] = 110
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "hum is out of range")

    def test_rain_out_of_range(self):
        data = self.valid_data.copy()
        data['measurements'][1]['label'] = 'rain'
        data['measurements'][1]['value'] = 3
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], "rain is out of range")

    def test_missing_datalogger(self):
        data = self.valid_data.copy()
        del data['datalogger']
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_missing_location(self):
        data = self.valid_data.copy()
        del data['location']
        response = self.client.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_invalid_json(self):
        response = self.client.post(self.url, '{"invalid_json":}', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())


class DataViewTests(TestCase):
    def setUp(self):
        self.datalogger = Datalogger.objects.create(id="c2a61e2e-068d-4670-a97c-72bfa5e2a58a")
        self.location = Location.objects.create(lat=47.56321, lng=1.524568)

        self.record = DataRecord.objects.create(at=parse_datetime("2024-12-24T12:00:00Z"), datalogger=self.datalogger, location=self.location)
        self.measurement = Measurement.objects.create(label="temp", value=22.5)
        self.record.measurements.add(self.measurement)

    def test_get_data_success(self):
        url = reverse('data')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('temp', str(response.content))
        self.assertIn('22.5', str(response.content))

    def test_missing_datalogger_param(self):
        url = reverse('data')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing required values."})

    def test_get_data_with_since_and_before(self):
        url = reverse('data')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'since': '2024-12-24T10:00:00Z',
                                         'before': '2024-12-24T13:00:00Z'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('temp', str(response.content))
        self.assertIn('22.5', str(response.content))

    def test_get_data_with_invalid_since(self):
        url = reverse('data')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'since': 'invalid-date'})

        self.assertEqual(response.status_code, 400)


class SummaryViewTests(TestCase):
    def setUp(self):
        self.datalogger = Datalogger.objects.create(id="c2a61e2e-068d-4670-a97c-72bfa5e2a58a")
        self.location = Location.objects.create(lat=47.56321, lng=1.524568)

        self.record1 = DataRecord.objects.create(
            at=parse_datetime("2024-12-24T12:00:00Z"), datalogger=self.datalogger, location=self.location)
        self.measurement1 = Measurement.objects.create(label="temp", value=22.5)
        self.measurement2 = Measurement.objects.create(label="rain", value=1.2)
        self.record1.measurements.add(self.measurement1, self.measurement2)

        self.record2 = DataRecord.objects.create(
            at=parse_datetime("2024-12-24T13:00:00Z"), datalogger=self.datalogger, location=self.location)
        self.measurement3 = Measurement.objects.create(label="temp", value=25.0)
        self.measurement4 = Measurement.objects.create(label="rain", value=0.8)
        self.record2.measurements.add(self.measurement3, self.measurement4)

        self.record3 = DataRecord.objects.create(
            at=parse_datetime("2024-12-23T10:00:00Z"), datalogger=self.datalogger, location=self.location)
        self.measurement5 = Measurement.objects.create(label="temp", value=18.0)
        self.measurement6 = Measurement.objects.create(label="rain", value=1.5)
        self.record3.measurements.add(self.measurement5, self.measurement6)

    def test_summary_no_span(self):
        url = reverse('summary')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 6)
        self.assertEqual(data[0]['label'], 'temp')
        self.assertEqual(data[0]['value'], 22.5)
        self.assertEqual(data[1]['label'], 'rain')
        self.assertEqual(data[1]['value'], 1.2)
        self.assertEqual(data[2]['label'], 'temp')
        self.assertEqual(data[2]['value'], 25.0)

    def test_summary_with_hour_span(self):
        url = reverse('summary')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'span': 'hour', 'since': '2024-12-24T01:00:00Z'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]['label'], 'temp')
        self.assertEqual(data[0]['time_slot'], "2024-12-24T12:00:00Z")
        self.assertEqual(data[0]['value'], 22.5)
        self.assertEqual(data[1]['label'], 'rain')
        self.assertEqual(data[1]['time_slot'], "2024-12-24T12:00:00Z")
        self.assertEqual(data[1]['value'], 1.2)
        self.assertEqual(data[2]['label'], 'temp')
        self.assertEqual(data[2]['time_slot'], "2024-12-24T13:00:00Z")
        self.assertEqual(data[2]['value'], 25.0)
        self.assertEqual(data[3]['label'], 'rain')
        self.assertEqual(data[3]['time_slot'], "2024-12-24T13:00:00Z")
        self.assertEqual(data[3]['value'], 0.8)

    def test_summary_with_day_span(self):
        url = reverse('summary')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'span': 'day', 'since': '2024-12-24T01:00:00Z'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['label'], 'temp')
        self.assertEqual(data[0]['time_slot'], "2024-12-24T00:00:00Z")
        self.assertEqual(data[0]['value'], 23.75)
        self.assertEqual(data[1]['label'], 'rain')
        self.assertEqual(data[1]['time_slot'], "2024-12-24T00:00:00Z")
        self.assertEqual(data[1]['value'], 2.0)

    def test_summary_with_rain_aggregation(self):
        url = reverse('summary')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'span': 'day', 'since': '2024-12-24T01:00:00Z'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        rain_data = [item for item in data if item['label'] == 'rain']
        self.assertEqual(len(rain_data), 1)
        self.assertEqual(rain_data[0]['value'], 2.0)

    def test_summary_with_temp_aggregation(self):
        url = reverse('summary')
        response = self.client.get(url, {'datalogger': 'c2a61e2e-068d-4670-a97c-72bfa5e2a58a', 'span': 'day', 'since': '2024-12-24T01:00:00Z'})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        temp_data = [item for item in data if item['label'] == 'temp']
        self.assertEqual(len(temp_data), 1)
        self.assertEqual(temp_data[0]['value'], 23.75)

    def test_summary_missing_datalogger_param(self):
        url = reverse('summary')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing required values."})
