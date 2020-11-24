import json
from time import sleep
import dateutil
import scrapy
from websocket import create_connection
from datetime import datetime


class RobobetSpider(scrapy.Spider):
    name = 'robobet'
    allowed_domains = ['roobet.com']
    start_urls = ['http://roobet.com/']

    curr = datetime.now()
    run_time = 7 * 24 * 60 * 60
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'FEED_FORMAT': 'csv',
        'FEED_URI': datetime.now().strftime('%Y_%m_%d__%H_%M') + '_robobet_items.csv'

    }
    headers = {
        'Pragma': 'no-cache',
        'Origin': 'https://roobet.com',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-WebSocket-Key': 'S/ZTgC7qrT9x77X8XAeSFA==',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 '
                      'Safari/537.36',
        'Upgrade': 'websocket',
        'Sec-WebSocket-Extensions': 'permessage-deflate; client_max_window_bits',
        'Cache-Control': 'no-cache',
        'Connection': 'Upgrade',
        'Sec-WebSocket-Version': '13',
    }
    headers = json.dumps(headers)

    def parse(self, response):
        headers = json.dumps(self.headers)
        ws = create_connection(
            'wss://api.roobet.com/socket.io/?EIO=3&transport=websocket', headers=headers, )

        while True:
            try:
                run_second = (datetime.now() - self.curr).seconds

                if run_second >= self.run_time:
                    return
                data = ws.recv()

                data = data.strip('42')
                results = {}
                if 'new_bet' in data:
                    data = json.loads(data)
                    data = data[1]
                    for k in data:
                        # print(k)
                        try:

                            if 'user' == k:
                                results['userName'] = data[k]['name']
                            else:
                                results[k] = data[k]
                        except Exception as e:

                            print(e)

                    results['Date'] = dateutil.parser.parse(
                        results['timestamp']).strftime('%m/%d/%y')
                    results['Time'] = dateutil.parser.parse(
                        results['timestamp']).strftime('%I:%M:%S %p')
                    del results['timestamp']
                    yield results
                    print('Total Run time: ', self.display_time(run_second))

                sleep(.5)
            except Exception as e:
                print(e)
                print("probably connection closed. Reconnectingc")
                try:
                    ws = create_connection(
                        'wss://api.roobet.com/socket.io/?EIO=3&transport=websocket', headers=headers, )
                except Exception as e:
                    self.logger.error(e)
    def display_time(self, seconds, granularity=2):
        intervals = (
            ('weeks', 604800),  # 60 * 60 * 24 * 7
            ('days', 86400),  # 60 * 60 * 24
            ('hours', 3600),  # 60 * 60
            ('minutes', 60),
            ('seconds', 1),
        )

        result = []

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds -= value * count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{} {}".format(value, name))
        return ', '.join(result[:granularity])
# userName	AmountBet	Date	Profit	Type	Balance_field	Game	Multiplyer	Won