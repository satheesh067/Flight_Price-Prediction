# Flight Price Prediction

Predict flight prices based on route, dates/times, airline, and stops using a trained machine learning model. This repo includes a Flask web app with authentication, history tracking, and CSV export, plus an optional Streamlit UI for experimentation.

## Tech Stack

- Backend: Flask, Flask-Login, Flask-SQLAlchemy (SQLite)
- ML: scikit-learn RandomForest (loaded from `model/flight_prediction.pkl`)
- Frontend: Bootstrap 5, custom CSS, vanilla JS

## Features

- User auth: register/login/logout (secure password hashing)
- Prediction dashboard (`/predict-page`) with dynamic inputs
- Save prediction history per user and export to CSV
- History page (`/history-page`) and JSON history API (`/history`)
- Simple REST endpoint for predictions (`POST /predict`)

## Project Structure (key files)

- `flask_app.py` – main Flask application (routes, DB models, auth, prediction)
- `model/flight_prediction.pkl` – trained model used for inference
- `templates/` – HTML templates (login, register, index, history, etc.)
- `static/css/auth.css` – shared modern styles for auth pages

## Setup

1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Set a secret key for sessions:

```bash
$env:SECRET_KEY = "your-secret-key"   # PowerShell on Windows
# or
export SECRET_KEY="your-secret-key"   # macOS/Linux
```

4. Run the Flask app:

```bash
python flask_app.py
```

The app will initialize the SQLite DB (`flight_predictions.db`) on first run and start in debug mode.

## Using the App

- Visit `/register` to create an account, then `/login`.
- Go to `/predict-page` to make predictions.
- View your `/history-page` or export CSV via `/export`.

## Prediction API

Endpoint: `POST /predict` (requires authentication)

Request JSON:

```json
{
  "source": "Delhi",
  "destination": "Cochin",
  "airline": "IndiGo",
  "stops": 1,
  "departure": "2025-10-17T08:30:00",
  "arrival": "2025-10-17T12:10:00"
}
```

Response JSON:

```json
{
  "success": true,
  "price": 5234.75,
  "duration": { "hours": 3, "minutes": 40 }
}
```

## Optional: Streamlit UI

A simple Streamlit interface exists in `app.py` for experimentation.

```bash
streamlit run app.py
```

Note: Ensure the model path in `app.py` points to `model/flight_prediction.pkl` on your machine.

## Screenshots

Add screenshots to `assets/` and reference them here, for example:

```html
<img src="assets/1.png" width="700"/>
<img src="assets/2.png" width="700"/>
```

## License

This project follows the [MIT License](https://choosealicense.com/licenses/mit/).
