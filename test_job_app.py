import os, io
from app import app

client = app.test_client()

# Prepare form data
form_data = {
    'role': 'Test Role',
    'first_name': 'John',
    'last_name': 'Doe',
    'email': 'john@example.com',
    'phone': '1234567890',
    'linkedin': 'https://linkedin.com/in/johndoe',
    'portfolio': '',
    'city': 'City',
    'state': 'State',
    'country': 'India',
    'exp_title[]': ['Engineer'],
    'exp_company[]': ['Company'],
    'exp_start[]': ['2022-01'],
    'exp_end[]': ['2023-01'],
    'edu_school[]': ['University'],
    'edu_degree[]': ['B.Tech'],
    'edu_major[]': ['CS'],
    'skills': 'Python, Flask',
    'cover_letter': 'Cover letter text',
    'agree': 'on',
    'authorized': 'on'
}
# Dummy resume file
resume_content = b'Hello resume content'
form_data['resume'] = (io.BytesIO(resume_content), 'resume.pdf')

response = client.post('/job-application', data=form_data, content_type='multipart/form-data', follow_redirects=True)
print('Status code:', response.status_code)
# Check if redirected to careers page (status code 200 after redirect)
print('Response snippet:', response.data[:200].decode('utf-8', errors='ignore'))
