class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    r6_user = db.Column(db.String(64), index=True)
    ubi_id = db.Column(db.String(64), index=True)
    plat_id = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    avatar = db.Column(db.String(94))

    uplay_data = db.relationship('Data', backref='author', lazy='dynamic')
    clan_id = db.Column(db.Integer, db.ForeignKey('clan.id'))
    gifs = db.relationship('Gif', backref='author', lazy='dynamic')

    twitch = db.Column(db.String(80), nullable=True)
    youtube = db.Column(db.String(80), nullable=True)
    mixer = db.Column(db.String(80), nullable=True)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.r6_user}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=32)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def join_clan(self, clan_id):
        self.clan = clan_id

    def leave_clan(self):
        self.clan = None

    def is_admin(self):
        if self.clan:
            return self.id == self.clan.clan_admin
        else:
            return False

    def set_region(self, region_id):
        self.region = region_id


class Clan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    clan_name = db.Column(db.String(128), index=True, unique=True)
    clan_avatar = db.Column(db.String(128))
    clan_admin = db.Column(db.Integer, index=True, unique=True)
    users = db.relationship('User', backref='clan', lazy='dynamic')

    def set_admin(self, user):
        self.clan_admin = user.id

    def set_avatar(self, clan_name):
        self.clan_avatar = f'{tiny}{clan_name.replace(" ", "%20")}{graphs}'

    def delete_clan(self):
        for u in self.users:
            u.leave_clan()

    def __repr__(self):
        return f'<Clan: {self.clan_name}>'


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_played = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    kd_ratio = db.Column(db.Float(asdecimal=True, decimal_return_scale=2))
    wl_ratio = db.Column(db.Float(asdecimal=True, decimal_return_scale=2))
    waifu = db.Column(db.String(64))
    rank = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    last_updated = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Data for: {self.author}>'


class Gif(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frame = db.Column(db.String(256))
    mp4 = db.Column(db.String(256))
    webm = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Gif {self.id} for: {self.author}.>'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
