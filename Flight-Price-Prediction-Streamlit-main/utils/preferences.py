from flask_login import current_user
from datetime import datetime

class UserPreferences:
    @staticmethod
    def get_default_settings():
        return {
            'currency': 'INR',
            'chart_type': 'line',
            'notification_enabled': True,
            'notification_frequency': 'immediate',
            'price_format': '₹{:,.2f}',
            'date_format': '%Y-%m-%d %H:%M',
            'theme': 'light'
        }

    @staticmethod
    def format_price(price, currency='INR'):
        if currency == 'INR':
            return f'₹{price:,.2f}'
        elif currency == 'USD':
            return f'${price:,.2f}'
        elif currency == 'EUR':
            return f'€{price:,.2f}'
        return f'{price:,.2f}'

    @staticmethod
    def format_datetime(dt, format='%Y-%m-%d %H:%M'):
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt)
        return dt.strftime(format)

    @staticmethod
    def get_chart_options(chart_type='line'):
        base_options = {
            'responsive': True,
            'plugins': {
                'legend': {
                    'position': 'top',
                },
                'tooltip': {
                    'mode': 'index',
                    'intersect': False,
                }
            }
        }
        
        if chart_type == 'line':
            return {
                **base_options,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Price (₹)'
                        }
                    },
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Date'
                        }
                    }
                }
            }
        elif chart_type == 'bar':
            return {
                **base_options,
                'scales': {
                    'y': {
                        'beginAtZero': True,
                        'title': {
                            'display': True,
                            'text': 'Price (₹)'
                        }
                    }
                }
            }
        return base_options