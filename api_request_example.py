TICKET = Ticket.query.first()


# Required for requesting authorisation ticket
def get_basic_token(email, password):
    return 'Basic ' + base64.b64encode((f'{email}:{password}').encode("utf-8")).decode("utf-8")


# Requests ticket from Ubi for API access
def get_ticket():
    app.logger.debug('Requesting ticket.')
    url = 'https://connect.ubi.com/ubiservices/v2/profiles/sessions'
    key = get_basic_token(os.environ['R6_USER'], os.environ['R6_KEY'])
    headers = {'Authorization': key,
               'Ubi-AppId': APPID,
               'Content-Type': 'application/json'}
    # sending post request and saving response as response object
    r = requests.post(url=url, headers=headers).json()
    app.logger.debug('Ticket recieved.')
    TICKET.value = f'Ubi_v1 t={r["ticket"]}'  # Adds prerequisite to the ticket data
    TICKET.created = datetime.now()
    db.session.commit()

# Checks if the ticket is present, or is older than ~3 hours (validity), requests a new one
def valid_ticket():
    if TICKET.is_valid():
        return TICKET.value
    else:
        app.logger.debug('Ticket expired. Requesting new ticket.')
        get_ticket()
        return TICKET.value


# Default headers for most API requests
headers = {'Authorization': valid_ticket(),
           'Ubi-AppId': APPID
           }


# Returns rank stats of the requested region. Limited to a single region per req
def get_rank(users, region, platform):
    url = f'https://public-ubiservices.ubi.com/v1/spaces/{PLATFORM_URL[platform]}/r6karma/players?'
    params = {
        'profile_ids': users,
        'board_id': 'pvp_ranked',
        'region_id': region,
        'season_id': '-1'
        }
    return requests.get(url=url, params=params, headers=headers).json()


# Returns uPlay username with correct formatting, and uPlay ID used for stat requests
def get_uplay_data(username, platform):
    url = 'https://public-ubiservices.ubi.com/v2/profiles?'
    params = {
        'nameOnPlatform': username,
        'platformType': platform
        }
    return requests.get(url=url, params=params, headers=headers).json()


# Returns all requested stats in the stat_list
def get_stats(users, stat_list, platform):
    url = f'https://public-ubiservices.ubi.com/v1/spaces/{PLATFORM_URL[platform]}/playerstats2/statistics?'
    params = {
        'populations': users,
        'statistics': stat_list
        }
    return requests.get(url=url, params=params, headers=headers).json()