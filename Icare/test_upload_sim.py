import os, django
from io import BytesIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Icare.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User

# ensure a user exists
if not User.objects.filter(username='testuser').exists():
    User.objects.create_user('testuser','test@example.com','pass1234')

client = Client()
client.login(username='testuser', password='pass1234')

# test non-csv file
f = BytesIO(b'just some data')
f.name = 'report.pdf'
response = client.post('/dashboard/', {'csv_file': f}, format='multipart')
print('non-csv status', response.status_code)
print('non-csv message present?', b'File uploaded successfully' in response.content)

# test csv file
g = BytesIO(b'age,gender\n30,Male\n')
g.name = 'data.csv'
response2 = client.post('/dashboard/', {'csv_file': g}, format='multipart')
print('csv status', response2.status_code)
print('csv prediction present?', b'Successfully analyzed' in response2.content)
