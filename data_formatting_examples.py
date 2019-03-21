def format(s):
    """ Takes seconds data and formats it into
        days, hours, minutes and seconds """
    minutes, seconds = divmod(s, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    if s < 3600:
        return f'{minutes}m'
    elif s < 86400:
        return f'{hours}h {minutes}m'
    else:
        return f'{days}d {hours}h {minutes}m'


def thousand(int):
    """ Formats large numbers to be more readable
        with thousand comma seperation """
    return ('{:,}'.format(int))


app.jinja_env.filters['format'] = format
app.jinja_env.filters['thousand'] = thousand
