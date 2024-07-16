
CREATE TABLE IF NOT EXISTS LicenseKeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    licensekey TEXT(64)
);

CREATE TABLE IF NOT EXISTS Devices (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	hostid TEXT(40),
	hostid2 TEXT(65),
	hostname TEXT(32),
	os TEXT(20),
	distro TEXT(20),
	distro_version TEXT(20),
	licensekey TEXT(64),
	lynis_version TEXT(10),
	last_update TEXT(20),
	compliance INTEGER,
	warnings INTEGER
);

CREATE TABLE IF NOT EXISTS FullReports (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	device_id INTEGER,
    full_report TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);