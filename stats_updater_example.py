def updater(users, region, platform):
    request_list = []
    for u in users:
        request_list.append(u.plat_id)

    request = get_stats(request_list, region, platform)
    for u in users:
        new_data = request[u.plat_id]
        u.avatar = get_avatar(u.ubi_id)
        data = Data.query.filter_by(author=u).first()
        data.time_played = new_data['generalpvp_timeplayed:infinite']
        data.kills = new_data['generalpvp_kills:infinite']
        data.deaths = new_data['generalpvp_death:infinite']
        data.wins = new_data['generalpvp_matchwon:infinite']
        data.losses = new_data['generalpvp_matchlost:infinite']
        data.kd_ratio = new_data['generalpvp_kd']
        data.wl_ratio = new_data['generalpvp_wl']
        data.waifu = new_data['waifu_name']
        data.rank = new_data['current_rank']
        data.author = u
        data.last_updated = datetime.utcnow()
        db.session.commit()


if __name__ == '__main__':
    for r in Region.query.all():
        for p in Platform.query.all():
            users = [i for i in p.users.all() if i in r.users.all()]
            if len(users) > 0:
                updater(users, r.ident, p.ident)
    app.logger.info('Stats updated.')
    calc()
    exit()
