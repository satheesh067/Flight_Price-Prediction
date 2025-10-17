@app.route('/analytics')
@login_required
def get_analytics():
    # Get user's prediction history
    predictions = PredictionHistory.query.filter_by(user_id=current_user.id).all()
    predictions_data = [{
        'timestamp': p.timestamp.isoformat(),
        'source': p.source,
        'destination': p.destination,
        'airline': p.airline,
        'stops': p.stops,
        'price': p.predicted_price
    } for p in predictions]
    
    # Get user's alerts
    alerts = PriceAlert.query.filter_by(user_id=current_user.id).all()
    alerts_data = [{
        'source': a.source,
        'destination': a.destination,
        'airline': a.airline,
        'max_price': a.max_price,
        'is_active': a.is_active
    } for a in alerts]
    
    # Calculate analytics
    analytics = {
        'price_trends': FlightAnalytics.calculate_price_trends(predictions_data),
        'alerts_summary': FlightAnalytics.get_price_alerts_summary(alerts_data),
        'best_deals': FlightAnalytics.predict_best_deals(predictions_data)
    }
    
    return jsonify(analytics)

@app.route('/route-analytics')
@login_required
def get_route_analytics():
    source = request.args.get('source')
    destination = request.args.get('destination')
    
    if not source or not destination:
        return jsonify({'error': 'Source and destination are required'}), 400
    
    predictions = PredictionHistory.query.filter_by(
        user_id=current_user.id,
        source=source,
        destination=destination
    ).all()
    
    predictions_data = [{
        'timestamp': p.timestamp.isoformat(),
        'airline': p.airline,
        'price': p.predicted_price
    } for p in predictions]
    
    analytics = {
        'route_stats': FlightAnalytics.get_route_analytics(predictions_data, source, destination),
        'best_booking_time': FlightAnalytics.get_best_booking_time(predictions_data, source, destination),
        'airline_comparison': FlightAnalytics.get_airline_comparison(predictions_data, source, destination)
    }
    
    return jsonify(analytics)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    if request.method == 'POST':
        data = request.json
        current_user.settings = {
            'currency': data.get('currency', 'INR'),
            'chart_type': data.get('chart_type', 'line'),
            'notification_enabled': data.get('notification_enabled', True),
            'notification_frequency': data.get('notification_frequency', 'immediate'),
            'theme': data.get('theme', 'light')
        }
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify(current_user.settings or UserPreferences.get_default_settings())