import datetime as dt


def year(request):
    cur_year = dt.date.today()
    cur_year = cur_year.strftime('%d/%m/%Y')
    cur_year = cur_year.split('/')
    return {'year': int(cur_year[-1])}
