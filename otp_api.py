from flask import request, jsonify
from time import time
from random import randint
import pyodbc



def configure_otp_api(app, cursor, redis_client):
    @app.route('/get_otp', methods=['POST'])
    def get_otp():
        try:
            data = request.get_json()
            mobile_number = data.get('mobile_number')

            if not mobile_number:
                return jsonify({'success': False, 'message': 'Mobile number is required'}), 400

            cursor.execute("SELECT COUNT(*) FROM users WHERE mobile_number=?", mobile_number)
            user_count = cursor.fetchone()[0]

            if user_count == 0:
                return jsonify({'success': False, 'message': 'User does not exist. Please create an account'}), 400 

            otp_count_key = f'otp_count:{mobile_number}'
            otp_count = redis_client.get(otp_count_key)

            if not redis_client.exists(otp_count_key):
                redis_client.set(otp_count_key, 0)

            otp_count = int(redis_client.get(otp_count_key))

            print(f'Current OTP count for {mobile_number}: {otp_count}') 

            if otp_count and int(otp_count) >=3:
                return jsonify({'success': False, 'message': 'Maximum OTP limit reached for this session'}), 400

            hardcoded_otp = str(randint(1000, 9999))

            otp_key = f'otp:{mobile_number}'
            redis_client.setex(otp_key, 120, hardcoded_otp)

            redis_client.incr(otp_count_key)

            response_data = {'success': True, 'message': 'OTP sent successfully'}
            return jsonify(response_data)

        except pyodbc.ProgrammingError as e:
            error_message = str(e)
            return jsonify({'success': False, 'message': f'SQL error: {error_message}'}), 500


    @app.route('/validate_otp', methods=['POST'])
    def validate_otp():
        data = request.get_json()
        mobile_number = data.get('mobile_number')
        user_entered_otp = data.get('otp')

        if not mobile_number or not user_entered_otp:
            return jsonify({'success': False, 'message': 'Mobile number and OTP are required'}), 400


        otp_key = f'otp:{mobile_number}'
        stored_otp = redis_client.get(otp_key)

        print(f'stored_otp: {stored_otp}, user_entered_otp: {user_entered_otp}')  


        if not stored_otp or stored_otp != user_entered_otp:
            return jsonify({'success': False, 'message': 'Invalid OTP'}), 400

        redis_client.delete(otp_key)

        otp_count_key = f'otp_count:{mobile_number}'
        redis_client.delete(otp_count_key)

        return jsonify({'success': True, 'message': 'OTP validated successfully'})