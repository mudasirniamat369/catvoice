import sqlite3
db = sqlite3.connect('tcv.db')
db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('followers', '19.6K')")
db.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('peak_views', '4.1M')")
db.commit()
db.close()
print("Done - followers and peak_views settings added to database")
