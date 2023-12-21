from flask import request, jsonify
import pyodbc

def configure_registration_api(app, cursor, sql_conn):
    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            name = data.get('name')
            age = data.get('age')
            city = data.get('city')
            height = data.get('height')
            weight = data.get('weight')
            mobile_number = data.get('mobile_number')

            cursor.execute("SELECT COUNT(*) FROM users WHERE mobile_number=?", mobile_number)
            user_count = cursor.fetchone()[0]

            if user_count > 0:
                return jsonify({'success': False, 'message': 'User already exists with this mobile number'}), 400
            
            cursor.execute("""
                INSERT INTO users (name, age, city, height, weight, mobile_number)
                VALUES (?, ?, ?, ?, ?, ?)
            """, name, age, city, height, weight, mobile_number)

            sql_conn.commit()

            response_data = {'success': True, 'message': 'User registered successfully'}
            return jsonify(response_data)
    
        except Exception as e:
            error_message = str(e)
            response_data = {'success': False, 'message': f'Registration failed. {error_message}'}
            return jsonify(response_data), 500
