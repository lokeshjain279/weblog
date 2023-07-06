from flask import Flask, request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import func, desc, text
from tabulate import tabulate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@1localhost:5432/kafka_log"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# API model class that defines the format of an object by listing all expected fields
class Weblog(db.Model):
    __tablename__ = 'weblogdb'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String())
    time = db.Column(db.DateTime)
    url = db.Column(db.String())
    status = db.Column(db.String())
    method = db.Column(db.String())
    # http = db.Column(db.Enum('HTTP/1.0','HTTP/1.1', name='http_types'), server_default="HTTP/1.1")
    http = db.Column(db.String())

    def __init__(self, ip, time, url, status, method, http):
        self.ip = ip
        self.time = time
        self.url = url
        self.status = status
        self.method = method
        self.http = http

    def __repr__(self):
        return f"<Entry {self.ip, self.time, self.url, self.status, self.method, self.http}>"

@app.route('/')
def hello():
    return {"Web-Log": "Analysis"}


@app.route('/weblog', methods=['GET'])
def handle_logs():
    if request.method == 'GET':
        # 1.Peak time for GET and POST request

        get_peak_time = (db.session.query(Weblog.time, func.count(Weblog.http).label('qty')
                              ).filter(Weblog.method=='GET').group_by(Weblog.time).order_by(desc('qty')).first())

        post_peak_time = (db.session.query(Weblog.time, func.count(Weblog.http).label('qty')
                                          ).filter(Weblog.method == 'POST').group_by(Weblog.time).order_by(
            desc('qty')).first())
        print(get_peak_time, "= Most no. of GET requests, at time = ", get_peak_time[0].ctime())

        #2.Hour-wise frequency of logs

        frequency=db.session.query(func.extract('hour', Weblog.time).label('h'),func.count(Weblog.http)).group_by('h').all()
        print('Hourwise frequency of logs:')
        hours = sorted(frequency, key=lambda x: x[0])
        hour_wise_freq=list(zip(*hours))[-1]

        # 5 most requested URL
        urls = db.session.query(Weblog.url, func.count(Weblog.url).label('freq')
                                ).group_by(Weblog.url).order_by(desc('freq')).limit(5).all()
        print(tabulate(urls, headers=['URL', 'freq.']))


        # Return all logs
        logs = Weblog.query.all()
        results = [
            {
                "ip": log.ip,
                "url": log.url,
                "time": log.time,
                "status": log.status,
                "method": log.method,
                "http": log.http
            } for log in logs]

        return {"5 Most requested URLS": urls, "Hour wise freuency of logs": hour_wise_freq, "peak-time for GET": get_peak_time,"Peak Time for POST": post_peak_time}

@app.route('/logcount', methods=['GET'])
def num_of_logs():
    # Number of logs at a given time
    time = request.args.get('time')
    time = time.replace('"','')
    print("TIME is", time)

    log_count = Weblog.query.filter_by(time=time).count()

    return {"Given Time ": time, "No. of logs ": log_count }


@app.route('/ratio', methods=['GET'])
def ratio():
    # Ratio of Status code 200 vs other status code for a given URL

    url = request.args.get('url')
    print("URL is", url)
    status_200 = db.session.query(func.count(Weblog.id)).filter(Weblog.status == '200').filter(Weblog.url == url).first()
    status_not200 = db.session.query(func.count(Weblog.id)).filter(Weblog.status != '200').filter(Weblog.url == url).first()
    result=0
    if status_not200[0] != 0:
        result = status_200[0] / status_not200[0]

    print('The ratio of Status code 200 vs other status code for a given URL =', result)
    print('\n')

    return {"Ratio of Status code 200 vs other status code is": result}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
