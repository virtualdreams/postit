# Run
uwsgi -s /var/run/uwsgi.socket --plugin python --callable app --wsgi-file app.py --master --threads 4 --gid www-data --uid www-data