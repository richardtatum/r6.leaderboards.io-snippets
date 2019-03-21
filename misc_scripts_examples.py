# Migrate admin script for selecting a new admin
def select_migrate_admin(clan, user):  # Select admin migrate (for choosing a new admin)
    if user.clan == clan:  # If user is a member of the current clan
        if not user.is_admin():  # User is not currently the admin
            clan.set_admin(user)
            db.session.commit()


# Migrate admin script for auto selecting new admin when someone deletes their account
def auto_migrate_admin(user):  # Auto admin migrate (for when an admin deletes their account)
    if user.is_admin():  # if user is admin of a clan
        if len(user.clan.users.all()) > 1:  # and the clan contains more than one person
            for u in user.clan.users.all():  # forloop through the users
                if u != user:  # first user that is not current_user
                    user.clan.set_admin(u)  # pass the admin rights to them


# User delete script
def user_delete(user):
    if user.clan:
        auto_migrate_admin(user)
        if len(user.clan.users.all()) is 1:  # if user is the last member in the clan
            db.session.delete(user.clan)  # delete the clan
    user.leave_clan  # finally, set user.clan to None

    for i in [Data, Weekly, Diff]:  # deletes every data set that connects to the user
        i = i.query.filter_by(author=user).first()
        db.session.delete(i)

    gifs = Gif.query.filter_by(author=user).all()
    for g in gifs:
        db.session.delete(g)

    db.session.delete(user)  # finally, delete the user
    db.session.commit()  # commit changes to the database


# Profanity Filer and custom removals
pf = ProfanityFilter(no_word_boundaries=True)
pf.remove_word('ass')
pf.remove_word('Fu')

# Region list for drop down on registrations/edit profile
regions = []
for r in Region.query.all():
    regions.append((r.ident, r.name))