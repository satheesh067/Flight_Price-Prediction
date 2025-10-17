import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FlightAnalytics:
    @staticmethod
    def calculate_price_trends(predictions):
        df = pd.DataFrame(predictions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.sort_values('timestamp', inplace=True)
        
        # Daily average prices
        daily_prices = df.groupby(df['timestamp'].dt.date)['price'].agg(['mean', 'min', 'max']).reset_index()
        daily_prices.columns = ['date', 'avg_price', 'min_price', 'max_price']
        
        return daily_prices.to_dict('records')

    @staticmethod
    def get_route_analytics(predictions, source=None, destination=None):
        df = pd.DataFrame(predictions)
        
        if source and destination:
            df = df[(df['source'] == source) & (df['destination'] == destination)]
        
        route_stats = {
            'avg_price': df['price'].mean(),
            'min_price': df['price'].min(),
            'max_price': df['price'].max(),
            'price_std': df['price'].std(),
            'total_predictions': len(df),
            'airlines': df['airline'].value_counts().to_dict(),
            'popular_times': df.groupby(pd.to_datetime(df['timestamp']).dt.hour)['price'].mean().to_dict()
        }
        
        return route_stats

    @staticmethod
    def get_best_booking_time(predictions, source, destination):
        df = pd.DataFrame(predictions)
        df = df[(df['source'] == source) & (df['destination'] == destination)]
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        
        hourly_avg = df.groupby('hour')['price'].mean()
        best_hour = hourly_avg.idxmin()
        worst_hour = hourly_avg.idxmax()
        
        return {
            'best_time': f"{best_hour:02d}:00",
            'worst_time': f"{worst_hour:02d}:00",
            'best_price': hourly_avg[best_hour],
            'worst_price': hourly_avg[worst_hour],
            'savings_potential': hourly_avg[worst_hour] - hourly_avg[best_hour]
        }

    @staticmethod
    def get_airline_comparison(predictions, source, destination):
        df = pd.DataFrame(predictions)
        df = df[(df['source'] == source) & (df['destination'] == destination)]
        
        airline_stats = df.groupby('airline').agg({
            'price': ['mean', 'min', 'max', 'std', 'count']
        }).reset_index()
        
        airline_stats.columns = ['airline', 'avg_price', 'min_price', 'max_price', 'price_std', 'flight_count']
        return airline_stats.to_dict('records')

    @staticmethod
    def get_price_alerts_summary(alerts):
        df = pd.DataFrame(alerts)
        
        summary = {
            'total_alerts': len(df),
            'active_alerts': len(df[df['is_active']]),
            'routes_watched': df.groupby(['source', 'destination']).size().to_dict(),
            'avg_target_price': df['max_price'].mean(),
            'most_watched_routes': df.groupby(['source', 'destination']).size().nlargest(5).to_dict()
        }
        
        return summary

    @staticmethod
    def predict_best_deals(predictions):
        df = pd.DataFrame(predictions)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        route_prices = df.groupby(['source', 'destination'])['price'].agg(['mean', 'std']).reset_index()
        route_prices['threshold'] = route_prices['mean'] - route_prices['std']
        
        good_deals = []
        for _, row in route_prices.iterrows():
            route_df = df[(df['source'] == row['source']) & 
                         (df['destination'] == row['destination']) &
                         (df['price'] < row['threshold'])]
            
            if not route_df.empty:
                good_deals.append({
                    'source': row['source'],
                    'destination': row['destination'],
                    'avg_price': row['mean'],
                    'deal_price': route_df['price'].min(),
                    'savings': row['mean'] - route_df['price'].min(),
                    'airline': route_df.loc[route_df['price'].idxmin(), 'airline']
                })
        
        return sorted(good_deals, key=lambda x: x['savings'], reverse=True)