import json
from django.test import TestCase
from pytz import timezone
from datetime import date, datetime, timedelta

from trends.service import trends_standard_get, trends_standard_post, process_trends_results


class TestProcessTrendsResults(TestCase):
    def setUp(self):
        with open('trends/tests/google_trends_explore_live_res.json') as f:
            self.response = json.load(f)

    def test_process_trends_results(self):
        expected_output = {
            'how cook': [
                {
                    "query": "how to cook fresh green beans",
                    "value": 14500
                },
                {
                    "query": "how to cook sugar snap peas",
                    "value": 10600
                },
                {
                    "query": "how long to cook corn on the cob in the microwave",
                    "value": 4050
                },
                {
                    "query": "how to cook brussel sprouts in air fryer",
                    "value": 3500
                },
                {
                    "query": "how to cook beef liver",
                    "value": 300
                },
                {
                    "query": "how long to cook chicken breast in oven at 350",
                    "value": 300
                },
                {
                    "query": "how long to cook a pre-cooked ham",
                    "value": 250
                },
                {
                    "query": "how to cook butternut squash",
                    "value": 250
                },
                {
                    "query": "how to cook adobong manok",
                    "value": 200
                },
                {
                    "query": "tim cook",
                    "value": 180
                },
                {
                    "query": "how to cook halibut",
                    "value": 170
                },
                {
                    "query": "how long to cook potatoes in oven",
                    "value": 150
                },
                {
                    "query": "how to cook spam",
                    "value": 150
                },
                {
                    "query": "how long to cook corned beef",
                    "value": 150
                },
                {
                    "query": "how to cook potatoes in the oven",
                    "value": 150
                },
                {
                    "query": "how to cook okra",
                    "value": 150
                },
                {
                    "query": "how long to cook pork tenderloin",
                    "value": 140
                },
                {
                    "query": "how to cook beets",
                    "value": 100
                },
                {
                    "query": "how to cook rump steak",
                    "value": 100
                },
                {
                    "query": "how long to cook corn on the grill",
                    "value": 100
                },
                {
                    "query": "how to cook oatmeal",
                    "value": 100
                },
                {
                    "query": "how to cook a rack of lamb",
                    "value": 100
                },
                {
                    "query": "how to cook broccolini",
                    "value": 100
                },
                {
                    "query": "how long do lentils take to cook",
                    "value": 90
                },
                {
                    "query": "how long to cook a whole chicken",
                    "value": 80
                }
            ],
            'recipe': [
                {
                    "query": "coronation quiche recipe",
                    "value": 32200
                },
                {
                    "query": "coronation chicken recipe",
                    "value": 180
                },
                {
                    "query": "collard greens recipe",
                    "value": 110
                },
                {
                    "query": "roasted carrots recipe",
                    "value": 90
                },
                {
                    "query": "quiche recipe",
                    "value": 80
                },
                {
                    "query": "best french toast recipe",
                    "value": 70
                },
                {
                    "query": "chicken piccata recipe",
                    "value": 70
                },
                {
                    "query": "toll house cookie recipe",
                    "value": 60
                },
                {
                    "query": "yorkshire pudding recipe",
                    "value": 60
                },
                {
                    "query": "oobleck recipe",
                    "value": 50
                },
                {
                    "query": "peanut butter cookie recipe",
                    "value": 50
                },
                {
                    "query": "best pancake recipe",
                    "value": 50
                },
                {
                    "query": "egg bites recipe",
                    "value": 50
                },
                {
                    "query": "fish taco recipe",
                    "value": 50
                },
                {
                    "query": "protein pancakes recipe",
                    "value": 50
                },
                {
                    "query": "salisbury steak recipe",
                    "value": 40
                },
                {
                    "query": "chipotle chicken recipe",
                    "value": 40
                },
                {
                    "query": "white chicken chili recipe",
                    "value": 40
                },
                {
                    "query": "cucumber salad recipe",
                    "value": 40
                },
                {
                    "query": "chicken pot pie recipe",
                    "value": 40
                },
                {
                    "query": "pot roast recipe",
                    "value": 40
                },
                {
                    "query": "glow recipe toner",
                    "value": 40
                },
                {
                    "query": "red beans and rice recipe",
                    "value": 40
                }
            ]
        }

        self.assertDictEqual(process_trends_results(self.response, ["how cook", "recipe"]), expected_output)


# If you don’t need to receive data in real-time, you can use the Standard method of data retrieval. The Standard
# method requires making separate POST and GET requests. Using this method, you can retrieve the results after our
# system collects them.

# Since Trending report runs every day, this will reduce price and prevent long running timeout errors

class TrendingReportTestCase(TestCase):
    def test_trends_standard_post_endpoint(self):
        tz = timezone('EST')
        end_date = datetime.now(tz)
        begin_date = end_date - timedelta(5)
        trending_results = trends_standard_post(begin_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        self.assertEqual(trending_results, True)

    def test_trends_standard_get_endpoint(self):
        # TODO: implement
        pass
