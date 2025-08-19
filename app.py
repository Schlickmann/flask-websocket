from flask import Flask, jsonify, request, send_file, render_template
from datetime import datetime, timedelta
from flask_socketio import SocketIO

from repository.database import db
from db_models.payment import Payment
from payments.pix import Pix

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
app.config['SECRET_KEY'] = 'SECRET_KEY_WEBSOCKET'
db.init_app(app)
socketio = SocketIO(app)

@app.route('/payments/pix', methods=['POST'])
def create_pix_payment():
    data = request.json

    if 'amount' not in data:
        return jsonify({'message': 'Amount is required'}), 400

    expiration_date = datetime.now() + timedelta(minutes=30)

    payment = Payment(
        amount=data['amount'],
        expiration_date=expiration_date
    )

    pix = Pix()
    payment_pix = pix.create_payment(data['amount'])

    payment.bank_payment_id = payment_pix['bank_payment_id']
    payment.qr_code = payment_pix['qr_code_path']

    db.session.add(payment)
    db.session.commit()

    return jsonify({'message': 'The payment has been created', 'payment': payment.to_dict()}), 200

@app.route('/payments/pix/qr_code/<string:file_name>', methods=['GET'])
def get_qr_code(file_name):
    return send_file(f'static/img/{file_name}.png', mimetype='image/png')

@app.route('/payments/pix/confirmation', methods=['POST'])
def pix_confirmation():
    data = request.json

    if 'bank_payment_id' not in data or 'amount' not in data:
        return jsonify({'message': 'Invalid payment data'}), 400

    payment = Payment.query.filter_by(bank_payment_id=data['bank_payment_id']).first()

    if not payment or payment.paid:
        return jsonify({'message': 'Payment not found'}), 404
    
    if payment.amount != data['amount']:
        return jsonify({'message': 'Invalid payment data'}), 400
    
    payment.paid = True
    db.session.commit()

    socketio.emit(f'payment_confirmed_{payment.id}')

    return jsonify({'message': 'The payment has been confirmed'}), 200

@app.route('/payments/pix/<int:payment_id>', methods=['GET'])
def payment_pix_page(payment_id):
    payment = Payment.query.get(payment_id)

    if not payment:
        return render_template('404.html')

    if payment.paid:
        return render_template('confirmed_payment.html', payment=payment)

    return render_template('payment.html', payment=payment, host="http://127.0.0.1:5000")

# WebSocket
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True)