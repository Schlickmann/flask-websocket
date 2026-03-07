# flask-websocket
A sample **PIX payment API** built with **Flask** and **Flask-SocketIO** that demonstrates real-time payment confirmation via WebSockets. When a payment is confirmed by the bank, the frontend is instantly notified through a WebSocket event — no polling required.
## Features
- Create a PIX payment with an auto-generated QR code
- Serve QR code images statically
- Confirm a payment via a bank callback endpoint
- Real-time payment confirmation pushed to the frontend using WebSockets (Socket.IO)
- Payment status page with automatic redirect on confirmation
- SQLite database for payment persistence (via SQLAlchemy)
- Unit tests with pytest
## Tech Stack
| Tool | Purpose |
|------|---------|
| [Flask](https://flask.palletsprojects.com/) | Web framework |
| [Flask-SocketIO](https://flask-socketio.readthedocs.io/) | WebSocket support |
| [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/) | ORM / database layer |
| [qrcode](https://pypi.org/project/qrcode/) | QR code generation |
| [Pillow](https://pillow.readthedocs.io/) | Image processing (required by qrcode) |
| [pytest](https://docs.pytest.org/) | Testing |
| SQLite | Default local database |
## Project Structure
```
flask-websocket/
├── db_models/
│   └── payment.py          # SQLAlchemy Payment model
├── payments/
│   └── pix.py              # PIX payment logic & QR code generation
├── repository/
│   └── database.py         # SQLAlchemy db instance
├── static/
│   ├── assets/             # Icons (tag, clock, basket SVGs)
│   ├── css/
│   │   └── styles.css      # Frontend styles
│   └── img/                # Generated QR code PNGs
├── templates/
│   ├── payment.html        # Payment page (shows QR code, listens for WS event)
│   ├── confirmed_payment.html  # Shown after payment is confirmed
│   └── 404.html            # Not found page
├── tests/
│   └── test_pix.py         # pytest tests for PIX payment logic
├── app.py                  # Flask app, routes, and SocketIO events
└── requirements.txt
```
## Getting Started
### 1. Clone the repository
```bash
git clone https://github.com/Schlickmann/flask-websocket.git
cd flask-websocket
```
### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the app
```bash
python app.py
```
The server starts on **http://127.0.0.1:5000** with debug mode enabled.
> The SQLite database (`payments.db`) is created automatically on first run inside the `instance/` folder.
## API Endpoints
### `POST /payments/pix` — Create a PIX payment
**Request body:**
```json
{
  "amount": 99.90
}
```
**Response `200`:**
```json
{
  "message": "The payment has been created",
  "payment": {
    "id": 1,
    "amount": 99.90,
    "paid": false,
    "bank_payment_id": "some-uuid",
    "qr_code": "qr_code_payment_some-uuid",
    "expiration_date": "2025-08-18T20:13:00"
  }
}
```
> Payments expire 30 minutes after creation.
---
### `GET /payments/pix/qr_code/<file_name>` — Get QR code image
Returns the QR code PNG file for the given filename.
---
### `POST /payments/pix/confirmation` — Confirm a payment (bank callback)
**Request body:**
```json
{
  "bank_payment_id": "some-uuid",
  "amount": 99.90
}
```
**Response `200`:**
```json
{
  "message": "The payment has been confirmed"
}
```
On success, marks the payment as paid and emits a `payment_confirmed_<id>` WebSocket event to all connected clients.
---
### `GET /payments/pix/<payment_id>` — Payment status page
Renders an HTML page showing the QR code and payment details. The page listens for the `payment_confirmed_<id>` WebSocket event and automatically reloads when the payment is confirmed, switching to the confirmation screen.
## How the WebSocket Flow Works
1. Client navigates to `/payments/pix/<payment_id>` — the page loads and opens a Socket.IO connection.
2. The page subscribes to the `payment_confirmed_<payment_id>` event.
3. The bank calls `POST /payments/pix/confirmation` when the payment goes through.
4. The server marks the payment as paid and emits `payment_confirmed_<payment_id>` via Socket.IO.
5. The client page receives the event and reloads, now rendering the `confirmed_payment.html` template.
## Running Tests
```bash
cd tests
pytest
```
The test suite verifies that the `Pix` class correctly generates a `bank_payment_id`, a `qr_code_path`, and saves the QR code PNG to disk.
