def safe_divide(x, y, n):
    try:
        return round(x/y, n)
    except ZeroDivisionError:
        return 0


def weekly_data(u):
    d = Data.query.filter_by(author=u).first()
    w = Weekly.query.filter_by(author=u).first()
    diff = Diff.query.filter_by(author=u).first()
    diff.time_played = (d.time_played - w.time_played)
    diff.kills = (d.kills - w.kills)
    diff.deaths = (d.deaths - w.deaths)
    diff.wins = (d.wins - w.wins)
    diff.losses = (d.losses - w.losses)
    diff.wl_ratio = safe_divide(diff.wins, (diff.wins + diff.losses), 3)*100
    diff.kd_ratio = safe_divide(diff.kills, diff.deaths, 2)
    db.session.commit()


def calc():
    users = User.query.all()
    for u in users:
        weekly_data(u)
