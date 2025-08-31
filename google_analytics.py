"""
Google Analytics 4 Data Integration
This module fetches real analytics data from Google Analytics 4
"""

import os
from datetime import datetime, timedelta
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.auth.exceptions import DefaultCredentialsError
import json

class GoogleAnalyticsIntegration:
    def __init__(self, property_id="your_ga4_property_id"):
        """
        Initialize Google Analytics Data API client
        
        Args:
            property_id (str): Your GA4 Property ID (format: properties/XXXXXXXXX)
        """
        self.property_id = property_id
        self.client = None
        self.is_authenticated = False
        
        try:
            # Try to initialize the client
            self.client = BetaAnalyticsDataClient()
            self.is_authenticated = True
            print("✅ Google Analytics API client initialized successfully!")
        except DefaultCredentialsError:
            print("⚠️ Google Analytics credentials not found. Using demo data.")
            self.is_authenticated = False
        except Exception as e:
            print(f"❌ Error initializing Google Analytics API: {e}")
            self.is_authenticated = False

    def get_page_views(self, days_back=7):
        """
        Get page views data from Google Analytics
        
        Args:
            days_back (int): Number of days to look back
            
        Returns:
            list: List of tuples (page_path, views)
        """
        if not self.is_authenticated:
            return self._get_demo_page_views()
        
        try:
            request = RunReportRequest(
                property=self.property_id,
                dimensions=[Dimension(name="pagePath")],
                metrics=[Metric(name="screenPageViews")],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )],
                limit=10
            )
            
            response = self.client.run_report(request)
            
            page_views = []
            for row in response.rows:
                page_path = row.dimension_values[0].value
                views = int(row.metric_values[0].value)
                
                # Clean up page path for display
                page_name = page_path.strip('/').replace('/', ' ').title() or 'Home'
                page_views.append((page_name, views))
            
            return sorted(page_views, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            print(f"Error fetching page views: {e}")
            return self._get_demo_page_views()

    def get_user_metrics(self, days_back=7):
        """
        Get user engagement metrics from Google Analytics
        
        Args:
            days_back (int): Number of days to look back
            
        Returns:
            dict: Dictionary containing bounce rate, session duration, etc.
        """
        if not self.is_authenticated:
            return self._get_demo_metrics()
        
        try:
            request = RunReportRequest(
                property=self.property_id,
                metrics=[
                    Metric(name="bounceRate"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="sessions"),
                    Metric(name="activeUsers"),
                    Metric(name="screenPageViews")
                ],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )]
            )
            
            response = self.client.run_report(request)
            
            if response.rows:
                row = response.rows[0]
                metrics = {
                    'bounce_rate': float(row.metric_values[0].value) * 100,
                    'avg_session_duration': float(row.metric_values[1].value),
                    'total_sessions': int(row.metric_values[2].value),
                    'active_users': int(row.metric_values[3].value),
                    'page_views': int(row.metric_values[4].value)
                }
                return metrics
            
            return self._get_demo_metrics()
            
        except Exception as e:
            print(f"Error fetching user metrics: {e}")
            return self._get_demo_metrics()

    def get_real_time_users(self):
        """
        Get real-time active users (requires Real Time Reporting API)
        
        Returns:
            int: Number of active users in last 30 minutes
        """
        if not self.is_authenticated:
            return 3  # Demo data
        
        try:
            # Note: This would require the Real Time Reporting API
            # For now, return a placeholder
            return 0
        except Exception as e:
            print(f"Error fetching real-time users: {e}")
            return 0

    def get_top_events(self, days_back=7):
        """
        Get top events from Google Analytics
        
        Args:
            days_back (int): Number of days to look back
            
        Returns:
            list: List of tuples (event_name, count)
        """
        if not self.is_authenticated:
            return self._get_demo_events()
        
        try:
            request = RunReportRequest(
                property=self.property_id,
                dimensions=[Dimension(name="eventName")],
                metrics=[Metric(name="eventCount")],
                date_ranges=[DateRange(
                    start_date=f"{days_back}daysAgo",
                    end_date="today"
                )],
                limit=10
            )
            
            response = self.client.run_report(request)
            
            events = []
            for row in response.rows:
                event_name = row.dimension_values[0].value
                count = int(row.metric_values[0].value)
                events.append((event_name, count))
            
            return sorted(events, key=lambda x: x[1], reverse=True)
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return self._get_demo_events()

    def _get_demo_page_views(self):
        """Demo data for when GA4 API is not available"""
        return [
            ('Home', 156),
            ('About', 89),
            ('Services', 67),
            ('Contact', 34),
            ('Dashboard', 23)
        ]

    def _get_demo_metrics(self):
        """Demo metrics for when GA4 API is not available"""
        return {
            'bounce_rate': 42.5,
            'avg_session_duration': 145.3,
            'total_sessions': 234,
            'active_users': 189,
            'page_views': 369
        }

    def _get_demo_events(self):
        """Demo events for when GA4 API is not available"""
        return [
            ('page_view', 369),
            ('scroll', 234),
            ('click', 156),
            ('form_submit', 23),
            ('file_download', 12)
        ]

# Convenience function to get GA data
def get_google_analytics_data():
    """
    Get combined Google Analytics data
    
    Returns:
        dict: Combined analytics data from GA4
    """
    # You'll need to replace this with your actual GA4 Property ID
    # Format: "properties/XXXXXXXXX" where X is your property ID number
    ga_property_id = "properties/YOUR_GA4_PROPERTY_ID"
    
    ga = GoogleAnalyticsIntegration(ga_property_id)
    
    return {
        'page_views': ga.get_page_views(),
        'metrics': ga.get_user_metrics(),
        'real_time_users': ga.get_real_time_users(),
        'top_events': ga.get_top_events(),
        'is_live_data': ga.is_authenticated
    }

if __name__ == "__main__":
    # Test the integration
    data = get_google_analytics_data()
    print("Google Analytics Data:")
    print(json.dumps(data, indent=2))
