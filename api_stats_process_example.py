# Takes username and returns username with correct formatting and uPlay/Platform ID
def get_username_id(username, platform):
    response = api.get_uplay_data(username, platform)['profiles'][0]
    app.logger.info(f'Username request for {username}.')
    return response['nameOnPlatform'], response['userId'], response['profileId']


# Combines all the stats, works out the k/d and w/l, adds waifu and rank and returns as a dict
def combine_stats(user_list, waifu, stats, rank):
    app.logger.info('Combining stats.')
    combined_dict = {}
    for u in user_list:
        x = stats['results'][u]
        x['generalpvp_wl'] = safe_divide(x['generalpvp_matchwon:infinite'],
                                         (x['generalpvp_matchwon:infinite'] +
                                         x['generalpvp_matchlost:infinite']), 3)*100
        x['generalpvp_kd'] = safe_divide(x['generalpvp_kills:infinite'],
                                         x['generalpvp_death:infinite'], 2)
        x['current_rank'] = rank['players'][u]['rank']
        x['waifu_name'] = get_waifu_name(waifu['results'][u])
        combined_dict[u] = x
    return combined_dict


# Main stat request function. Pulls together from all other functiosn to return combined stats
def get_stats(user_list, region, platform):
    app.logger.info(f'Stats requested for {region.upper()}, {platform.upper()}.')
    users = list_format(user_list)  # Required formatting for API request
    stats = list_format(stat_list)
    operators = api.get_operators(users, platform)
    stats = api.get_stats(users, stats, platform)
    rank = api.get_rank(users, region, platform)
    return combine_stats(user_list, operators, stats, rank)
