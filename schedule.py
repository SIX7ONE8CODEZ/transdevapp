from flask import request, jsonify
from app import app, db, mail

from flask_mail import Message
from database import Shift

@app.route('/create_shift', methods=['POST'])
def create_shift():
    employee_id = request.json['employee_id']
    start_time = request.json['start_time']
    end_time = request.json['end_time']

    new_shift = Shift(employee_id=employee_id, start_time=start_time, end_time=end_time)
    db.session.add(new_shift)
    db.session.commit()

    return jsonify({"message": "Shift created successfully!"}), 201

@app.route('/request_swap', methods=['POST'])
def request_swap():
    shift_id = request.json['shift_id']
    shift = Shift.query.get(shift_id)
    
    if shift:
        shift.status = "Swap Requested"
        db.session.commit()
        return jsonify({"message": "Shift swap requested!"}), 200
    
    return jsonify({"error": "Shift not found"}), 404

def send_notification(email, subject, message):
    msg = Message(subject, sender='your_email@example.com', recipients=[email])
    msg.body = message
    mail.send(msg)

@app.route('/notify_swap', methods=['POST'])
def notify_swap():
    shift_id = request.json['shift_id']
    shift = Shift.query.get(shift_id)

    if shift:
        employee_email = shift.employee.email
        send_notification(employee_email, "Shift Swap Request", f"Your shift on {shift.start_time} has a swap request.")
        return jsonify({"message": "Notification sent!"}), 200
    
    return jsonify({"error": "Shift not found"}), 404