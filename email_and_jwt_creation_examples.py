def get_invite_token(email, clan, expires_in=86400):
    return jwt.encode(
        {'email': email, 'clan_id': clan.id, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


def verify_invite_token(token):
    data = {}
    try:
        keys = ['email', 'clan_id']
        for key in keys:
            data[key] = jwt.decode(token, current_app.config['SECRET_KEY'],
                                   algorithms=['HS256'])[key]
    except:
        return
    return data


def send_email(app, recipients, sender=None, subject='', text='', html=''):
    ses = boto3.client(
        'ses',
        region_name=app.config['SES_REGION_NAME'],
        aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
    )
    if not sender:
        sender = app.config['SES_EMAIL_SOURCE']

    ses.send_email(
        Source=sender,
        Destination={'ToAddresses': recipients},
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Text': {'Data': text},
                'Html': {'Data': html}
                    }
                })
