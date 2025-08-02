import db
from flask import  Response
import csv
import io

def export_csv():
    con = db.get_connection()
    cur = con.cursor()
    cur.execute("SELECT * from monitoring.get_losses ORDER BY action_date")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Ім'я", "Email"])  # Заголовки

    for row in cur:
        writer.writerow(row)

    con.close()

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=losses.csv"
    return response