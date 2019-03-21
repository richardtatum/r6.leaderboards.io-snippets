class RegistrationForm(FlaskForm):
    r6_user = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    region = SelectField('Region', choices=regions, validators=[DataRequired()])
    platform = SelectField('Platform', choices=platforms, validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message='The new password fields do not match, please try again.')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_r6_user(self, r6_user):
        user = User.query.filter(User.r6_user.like(self.r6_user.data)).first()
        if user is not None:
            if user.platform.ident == self.platform.data:
                raise ValidationError('This username is already registered on this platform.')
        try:
            self.details = get_username_id(self.r6_user.data, self.platform.data)
        except IndexError:
            raise ValidationError('Username not found, please try again.')


class ClanRegistrationForm(FlaskForm):
    clan_name = StringField('Clan Name', validators=[DataRequired()])
    submit = SubmitField('Create Clan')

    def validate_clan_name(self, clan_name):
        if not re.match(r'^[A-Za-z\d ]*$', clan_name.data):
            raise ValidationError('Please use only alphanumeric characters.')
        clan = Clan.query.filter_by(clan_name=self.clan_name.data.lower()).first()
        if clan is not None:
            raise ValidationError('That name is taken, please pick a different clan name.')
        if pf.is_clean(clan_name.data) is not True:
            app.logger.info(f'Attempted registration of profane clan name: {clan_name.data}, by user:{current_user.r6_user} id:{current_user.id}')
            raise ValidationError('Name includes profanities. Please try another name.')


class AccountDeleteForm(FlaskForm):
    r6_user = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password', message="The password fields do not match, please try again.")])
    submit = SubmitField('DELETE MY ACCOUNT')

    def __init__(self, original_r6_user, *args, **kwargs):
        super(AccountDeleteForm, self).__init__(*args, **kwargs)
        self.original_r6_user = original_r6_user

    def validate_r6_user(self, r6_user):
        if r6_user.data.lower() != self.original_r6_user.lower():
            raise ValidationError('This username is incorrect.')


class GifUploadForm(FlaskForm):
    url = StringField('GfyCat URL', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_url(self, url):
        if 'gfycat.com' not in url.data:
            raise ValidationError('That is not a gfycat URL.')
        self.details = gfycat_url_format(url.data)
        if self.details is None:
            raise ValidationError('There was an error processing that clip. Please check the URL and try again.')
        if self.details['nsfw'] != 0:
            raise ValidationError('Your clip was deemed to be NSFW and will not be uploaded.')
            app.logger.info(f'NSFW gif upload attempted by {current_user}. Link: {details["webm"]}')

