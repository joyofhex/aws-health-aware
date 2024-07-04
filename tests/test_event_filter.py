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

        self.assertEqual(event_filter.event_types, ['issue'])

    def test_non_org_mode_filter(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "240"  # 240 hours = 10 days

        with patch('handler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 10, 30)
            event_filter = EventFilter(organization=False)
            result = event_filter.filter()

        self.assertEqual(
            result,
            {
                'eventTypeCategories': ['issue'],
                'lastUpdatedTimes': [{'from': datetime(2024, 10, 20, 0, 0)}]
            }
        )

    def test_org_mode_filter(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "240"  # 240 hours = 10 days

        with patch('handler.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 10, 30)
            event_filter = EventFilter(organization=True)
            result = event_filter.filter()

        self.assertEqual(
            result,
            {
                'eventTypeCategories': ['issue'],
                'lastUpdatedTime': [{'from': datetime(2024, 10, 20, 0, 0)}]
            }
        )

    def test_no_type_env_variable_set(self):
        if "HEALTH_EVENT_TYPE" in os.environ:
            del os.environ["HEALTH_EVENT_TYPE"]

        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.event_types, None)

    def test_incorrect_type_in_env_var_is_filtered(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue, investigation, nonExistingCategory"

        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.event_types, ['investigation', 'issue'])

    def test_previous_default_value(self):
        os.environ["HEALTH_EVENT_TYPE"] = "issue | accountNotification | scheduledChange"
        os.environ["REGIONS"] = "all regions"
        os.environ["EVENT_SEARCH_BACK"] = "300"
        event_filter = EventFilter()

        self.assertEqual(event_filter.event_types, None)


if __name__ == '__main__':
    unittest.main()
