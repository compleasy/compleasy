from flask import Flask, g, request, jsonify, render_template, url_for
import os
import logging
import sqlite3

APPDIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = APPDIR + '/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database location
DATABASE = APPDIR + '/compleasy.db'

# Class to parse Lynis reports
class LynisReport:
    def __init__(self, report_file_or_content):
        self.keys = {}
        if os.path.exists(report_file_or_content):
            with open(report_file_or_content, 'r') as file:
                self.report = file.read()
        else:
            self.report = report_file_or_content
        self.keys = self.parse_report()

    def get_full_report(self):
        return self.report

    def parse_report(self):
        for line in self.report.split('\n'):
            if not line:
                continue
            if line.startswith('#'):
                continue
            if '=' not in line:
                continue
            # If there are multiple '=' in the line, split only the first one
            key, value = line.split('=', 1)
            self.keys[key] = value
        # Add warnings and suggestions keys
        self.keys['count_warnings'] = self.count_warnings() or 0
        self.keys['count_suggestions'] = self.count_suggestions() or 0
        return dict(self.keys)
    
    def get(self, key):
        return self.keys.get(key)
    
    def count_warnings(self):
        return len([k for k in self.keys.keys() if k.startswith('warning[]')])
    
    def count_suggestions(self):
        return len([k for k in self.keys.keys() if k.startswith('suggestion[]')])

########################################################################################
# Database functions
########################################################################################

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def db_get_licenses(cursor):
    cursor.execute('SELECT * FROM LicenseKeys')
    licenses = cursor.fetchall()
    return licenses

def db_get_license(cursor, licensekey):
    cursor.execute('SELECT id FROM LicenseKeys WHERE licensekey = ?', (licensekey,))
    license = cursor.fetchone()
    if license:
        return license['id']
    return None

def db_get_devices(cursor):
    cursor.execute('SELECT * FROM Devices')
    devices = cursor.fetchall()
    return devices

def db_get_reports(cursor):
    cursor.execute('SELECT * FROM FullReports')
    reports = cursor.fetchall()
    return reports

def db_get_device_id(cursor, hostid, hostid2):
    cursor.execute('SELECT id FROM Devices WHERE hostid = ? AND hostid2 = ?', (hostid, hostid2))
    device = cursor.fetchone()
    if device:
        return device['id']
    return None

def db_new_device(cursor, hostid, hostid2):
    cursor.execute('''
            INSERT INTO Devices
                (hostid, hostid2)
                VALUES (?, ?)''',
            (hostid, hostid2))
    cursor.connection.commit()
    return cursor.lastrowid

def db_update_device(cursor, device):
    logging.info('Warnings: %s', device['count_warnings'])
    cursor.execute('''
            UPDATE Devices
                SET hostname = ?, os = ?, distro = ?, distro_version = ?, lynis_version = ?, last_update = ?, warnings = ?
                WHERE hostid = ? AND hostid2 = ?''',
            (device['hostname'], device['os'], device['os_name'], device['os_version'], device['lynis_version'], device['report_datetime_end'], device['count_warnings'], device['hostid'], device['hostid2']))
    cursor.connection.commit()
    return cursor.lastrowid

def db_store_full_report(cursor, device_id, full_report):
    cursor.execute('''
            INSERT INTO FullReports
                (device_id, full_report)
                VALUES (?, ?)''',
            (device_id, full_report))
    cursor.connection.commit()
    return cursor.lastrowid


########################################################################################
# Routes
########################################################################################

'''
Description: Initialize the database
Request: GET /admin/db/init
Payload: delete=<Boolean>
Response: 200 OK
'''
@app.route('/admin/db/init', methods=['GET'])
def init_db():
    if os.path.exists(DATABASE):
        if request.args.get('delete') and request.args.get('delete').lower() == 'true':
            # Delete full database
            os.remove(DATABASE)
            logging.info('Database deleted')
    
    db = get_db()
    with app.open_resource(APPDIR + '/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    logging.info('Database initialized')
    return 'Database initialized', 200

'''
Description: Add a license key
Request: POST /admin/license/add
Payload: licensekey=<license key>
Response: 200 OK
'''
@app.route('/admin/license/add', methods=['POST'])
def add_license():
    licensekey = request.form.get('licensekey')
    if licensekey:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO LicenseKeys (licensekey) VALUES (?)', (licensekey,))
        db.commit()
        return 'License key added', 200
    return 'No license key provided', 400

'''
Description: Upload a report
Request: POST /api/lynis/upload/
Payload: data=<report content>&licensekey=<license key>&hostid=<host id>&hostid2=<host id 2>
Response: 200 OK
'''
@app.route('/api/lynis/upload/', methods=['POST'])
def upload_report():
    report = request.form.get('data')
    licensekey = request.form.get('licensekey')
    hostid = request.form.get('hostid')
    hostid2 = request.form.get('hostid2')

    logging.debug('License key: %s', licensekey)
    logging.debug('Host ID: %s', hostid)

    # Get the database connection
    db = get_db()
    cursor = db.cursor()
    
    # Ensure all required data is provided
    if not report or not licensekey or not hostid or not hostid2:
        return "Missing data", 400  # Bad Request if any data is missing
    
    # Check the license validity
    if db_get_license(cursor, licensekey) is None:
        return "Invalid license key", 401
    
    # You can store the report to a database or a file
    with open(UPLOAD_FOLDER + '/report.txt', 'w') as file:
        file.write(report)
    
    # Parse the report
    lynis_report = LynisReport(UPLOAD_FOLDER + '/report.txt')
    hostid = lynis_report.get('hostid')
    hostid2 = lynis_report.get('hostid2')

    # Check if the hostids are not empty
    if not hostid or not hostid2:
        logging.error('Host ID not found in the report')
        return "Host ID not found", 400

    # Get device id (if exists) or create a new device
    device_id = db_get_device_id(cursor, hostid, hostid2)
    if not device_id:
        device_id = db_new_device(cursor, hostid, hostid2)
    
    # Store the full report in the database
    full_report = lynis_report.get_full_report()
    if not full_report:
        logging.error('Error reading full report')
        return "Error parsing report", 500

    try:
        db_store_full_report(cursor, device_id, full_report)
        logging.info('Full report stored for device: %s', lynis_report.get('hostname'))
    except Exception as e:
        logging.error('Error storing full report: %s', e)
        return "Error storing full report", 500
    
    # Update the device
    parsed_report = lynis_report.parse_report()
    try:
        db_update_device(cursor, parsed_report)
        logging.info('Device updated: %s', parsed_report['hostname'])
    except Exception as e:
        logging.error('Error updating device: %s. More details: %s', parsed_report['hostname'], e)
        return "Error updating device", 500

    # Return a success response
    return "OK", 200

'''
Description: Check the license key
Request: POST /api/lynis/license/
Payload: licensekey=<license key>&collector_version=<collector version>
Response:
- "Response 100": 200 OK
- "Response 500": 401 Unauthorized
'''
@app.route('/api/lynis/license/', methods=['POST'])
def license():
    licensekey = request.form.get('licensekey')
    collector_version = request.form.get('collector_version')
    response = None, 400

    if licensekey is None:
        logging.error('No license key provided')
        return 'No license key provided', 400
    logging.debug('License key: %s', licensekey)
    

    if collector_version is None:
        logging.error('No collector version provided')
        return 'No collector version provided', 400
    logging.debug('Collector version: %s', collector_version)

    #Check license validity
    db = get_db()
    cursor = db.cursor()
    if db_get_license(cursor, licensekey):
        logging.info('License key is valid')
        response = 'Response 100', 200
    else:
        logging.error('License key is invalid')
        response = 'Response 500', 401

    return response

@app.route('/api/licenses/', methods=['GET'])
def get_licenses():
    db = get_db()
    cursor = db.cursor()
    licenses = db_get_licenses(cursor)

    # Fetch column names
    columns = [column[0] for column in cursor.description]

    # Convert rows to list of dictionaries
    licenses = [dict(zip(columns, license)) for license in licenses]

    return jsonify(licenses)

@app.route('/api/reports/', methods=['GET'])
def get_reports():
    db = get_db()
    cursor = db.cursor()
    reports = db_get_reports(cursor)

    # Fetch column names
    columns = [column[0] for column in cursor.description]

    # Convert rows to list of dictionaries
    reports = [dict(zip(columns, report)) for report in reports]

    return jsonify(reports)

@app.route('/api/devices/', methods=['GET'])
def get_devices():
    db = get_db()
    cursor = db.cursor()
    devices = db_get_devices(cursor)

    # Fetch column names
    columns = [column[0] for column in cursor.description]

    # Convert rows to list of dictionaries
    devices = [dict(zip(columns, device)) for device in devices]

    return jsonify(devices)

@app.route('/', methods=['GET'])
def index():
    # Get devices from database
    db = get_db()
    cursor = db.cursor()
    devices = db_get_devices(cursor)

    for d in devices:
        logging.info('Device hostname: %s', d['hostname'])

    return render_template('index.html', devices=devices)

if __name__ == '__main__':
    logger = logging.getLogger()
    logger.name = 'Compleasy'
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    app.run(host='0.0.0.0', port=3000, ssl_context='adhoc', debug=True)