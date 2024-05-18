import json
from channels.generic.websocket import AsyncWebsocketConsumer
from influxdb_client import InfluxDBClient
import asyncio


class DataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.influxdb_client = InfluxDBClient(
            url='http://iot.mmr.systems:8086/', token='wxoi_yuT-G2GfujTM1QiyLbXic9ezxr9N_iL-NzM0f42uZwBn6tXQJZI3TvBjBq6r810vxkB9-xFFG2FQAUWsQ==', org='mmr.systems')
        self.query_api = self.influxdb_client.query_api()
        self.sending_data = True
        await self.send_data()

    async def disconnect(self, close_code):
        self.sending_data = False
        await self.influxdb_client.close()

    async def send_data(self):
        bucket = 'test-bucket'
        field = 'i1'
        measurement = 'Irms'

        while self.sending_data:  # Проверяем флаг перед каждой итерацией
            query = f'''
                from(bucket: "{bucket}")
                |> range(start: -2d)
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> filter(fn: (r) => r._field == "{field}")
                |> aggregateWindow(every: 1m, fn: max, createEmpty: false)
            '''
            tables = self.query_api.query(query, org='mmr.systems')
            points = []
            for table in tables:
                for record in table.records:
                    points.append(
                        {"time": record.get_time().isoformat(), "value": record.get_value()})
            await self.send(text_data=json.dumps(points))
            await asyncio.sleep(5)
