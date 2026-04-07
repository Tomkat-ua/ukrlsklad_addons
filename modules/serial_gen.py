from flask import render_template,request

from datetime import datetime
def gen_date():
    year = datetime.now().strftime("%y")
    match datetime.now().month:
        case 10:
            month = "A"
        case 11:
            month = "B"
        case 12:
            month = "C"
        case _:
            month = datetime.now().month
    return f"{year}{month}"


def generator():
    result = []
    prefix = ''
    serial_len = 0
    crow = 0
    date_ = gen_date()
    if request.method == 'POST':
        prefix = request.form.get('pref','').strip()
        serial_len = int(request.form.get('len','').strip())
        crow = int(request.form.get('crow', '0').strip() or 0)
        date_ = request.form.get('date', '0').strip() or gen_date()
        prefix_len = len(prefix)
        for n in range(1,crow + 1):
            tail = str(n)
            if prefix_len + len(tail) + len(date_) < serial_len:
                tail = tail.rjust(serial_len - prefix_len - len(date_),"0")
            result.append(prefix + date_ +tail)
    return render_template('serials_gen.html'
                           ,title = 'Генерація серійників'
                           ,data  = result
                           ,pref  = prefix
                           ,len   = serial_len
                           ,crow  = crow
                           ,date  = date_)




