import os
import unittest
from datetime import datetime
from unittest.mock import patch

from handler import EventFilter


class TestEventFilter(unittest.TestCase):
    def test_basic_non_org_mode(self):
        os.environ["HEALTH_EVENT_TYPE"] = ""
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.organization, False)
        self.assertEqual(event_filter.event_types, None)
        self.assertEqual(event_filter.regions, None)
        self.assertEqual(event_filter.time_delta, 300)

    def test_basic_org_mode(self):
        os.environ["HEALTH_EVENT_TYPE"] = ""
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter(organization=True)

        self.assertEqual(event_filter.organization, True)
        self.assertEqual(event_filter.event_types, None)
        self.assertEqual(event_filter.regions, None)
        self.assertEqual(event_filter.time_delta, 300)

    def test_set_regions(self):
        os.environ["HEALTH_EVENT_TYPE"] = ""
        os.environ["REGIONS"] = "us-east-1,eu-west-2,ap-south-1"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.regions, ['us-east-1', 'eu-west-2', 'ap-south-1'])

    def test_set_event_type_to_issue(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.event_types, ['issue', 'investigation'])

    def test_non_org_mode_filter(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "240" # 240 hours = 10 days

        with patch('handler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 10, 30)
            event_filter = EventFilter(organization=False)
            result = event_filter.filter()

        self.assertEqual(
            result,
            {
                'eventTypeCategories': ['issue', 'investigation'],
                'lastUpdatedTimes': [{'from': datetime(2024, 10, 20, 0, 0)}]
            }
        )

    def test_org_mode_filter(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "240" # 240 hours = 10 days

        with patch('handler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 10, 30)
            event_filter = EventFilter(organization=True)
            result = event_filter.filter()

        self.assertEqual(
            result,
            {
                'eventTypeCategories': ['issue', 'investigation'],
                'lastUpdatedTime': [{'from': datetime(2024, 10, 20, 0, 0)}]
            }
        )


if __name__ == '__main__':
    unittest.main()
