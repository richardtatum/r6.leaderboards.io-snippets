@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        region = Region.query.filter_by(ident=form.region.data).first()
        platform = Platform.query.filter_by(ident=form.platform.data).first()
        user = User(r6_user=form.details[0], email=form.email.data.lower(), plat_id=form.details[2],
                    ubi_id=form.details[1], platform=platform, region=region)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            init(user, region.ident, platform.ident)
            flash('Congratulations, you are now a registered user!', 'success')
            app.logger.info(f'Registration completed for {user}.')
            send_signup_email(user)
            return redirect(url_for('login'))
        except KeyError:
            form.r6_user.errors = ['Username found, but without any stats. Likely the Ubisoft account has been deleted.']
    return render_template('register.html', title='Register', form=form)



@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_password_token(token)
    if not user:
        abort(401)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/clan_invite/<token>', methods=['GET', 'POST'])
def accept_clan_invite(token):
    data = verify_invite_token(token)
    if not data:
        abort(401)
    user = User.query.filter_by(email=data['email']).first()
    clan = Clan.query.filter_by(id=data['clan_id']).first()
    if user and user.clan:
        if user.is_authenticated:
            flash(f'You are already in a clan. Please leave before accepting the invite to {clan.clan_name.title()}.', 'warning')
            return redirect(url_for('clan'))
        else:
            flash(f'You are already in a clan. Please login and leave before accepting the invite to {clan.clan_name.title()}.', 'warning')
            return redirect(url_for('login', next='/clan'))
    if current_user.is_authenticated and current_user.email == data['email']:
        current_user.join_clan(clan)
        db.session.commit()
        flash(f'You have successfully joined {clan.clan_name.title()}', 'success')
        return redirect(url_for('home'))
    else:
        logout_user()
    if user:
        flash(f'Login to accept the clan invite from {clan.clan_name.title()}', 'info')
        form = LoginForm()
        if form.validate_on_submit():
            if form.email.data == data['email']:
                if user.check_password(form.password.data):
                    login_user(user)
                    user.join_clan(clan)
                    db.session.commit()
                    flash(f'You have successfully joined {clan.clan_name.title()}', 'success')
                    return redirect(url_for('home'))
            else:
                form.email.errors=['Email does not match. Please enter the correct email and try again.']
        return render_template('login.html', title='Sign In', email=data['email'], form=form)
    else:
        form = RegistrationForm()
        if form.validate_on_submit():
            if form.email.data == data['email']:
                region = Region.query.filter_by(ident=form.region.data).first()
                platform = Platform.query.filter_by(ident=form.platform.data).first()
                user = User(r6_user=form.details[0], email=form.email.data.lower(),
                            plat_id=form.details[2], ubi_id=form.details[1],
                            platform=platform, region=region)
                user.set_password(form.password.data)
                user.join_clan(clan)
                db.session.add(user)
                try:
                    init(user, region.ident, platform.ident)
                    app.logger.info(f'Registration completed for {user} through clan invite.')
                    flash('Congratulations, you are now a registered user!', 'success')
                    send_signup_email(user)
                    return redirect(url_for('login'))
                except KeyError:
                    form.r6_user.errors = ['Username found, but without any stats. Likely the Ubisoft account has been deleted.']
            else:
                form.email.errors=['Email does not match. Please enter the correct email and try again.']
        return render_template('register.html', title='Register', form=form, email=data['email'])


@app.route('/clan/migrate_admin/<r6_user>')
@login_required
def migrate_admin(r6_user):
    if not current_user.is_admin():
        abort(403)
    user = User.query.filter_by(r6_user=r6_user).first()
    select_migrate_admin(current_user.clan, user)
    flash(f'{r6_user} is now the admin for {current_user.clan.clan_name.title()}', 'success')
    return redirect(url_for('home'))


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    profile_form = EditProfileForm(current_user.email, current_user.r6_user)
    pass_form = PasswordChangeForm(current_user)
    del_form = AccountDeleteForm(current_user.r6_user)
    original_r6 = current_user.r6_user
    if profile_form.validate_on_submit():
        current_user.email = profile_form.email.data
        current_user.region = Region.query.filter_by(ident=profile_form.region.data).first()
        current_user.twitch = profile_form.twitch.data
        current_user.youtube = profile_form.youtube.data
        current_user.mixer = profile_form.mixer.data
        if original_r6.lower() != profile_form.r6_user.data.lower():
            try:
                app.logger.info(f'R6_User changed for {current_user.id}, updating stats.')
                current_user.r6_user = profile_form.details[0]
                current_user.ubi_id = profile_form.details[1]
                current_user.plat_id = profile_form.details[2]
                # Runs the new username through the stats updater. Must be passed as a list
                # Weekly stats is run to reset everything to zero.
                weekly_updater([current_user], current_user.region.ident, current_user.platform.ident)
                updater([current_user], current_user.region.ident, current_user.platform.ident)
            except KeyError:
                profile_form.r6_user.errors = ['Username found, but without any stats. Likely the Ubisoft account has been deleted.']
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        profile_form.region.process_data(current_user.region.ident)
        profile_form.email.data = current_user.email
        profile_form.twitch.data = current_user.twitch
        profile_form.youtube.data = current_user.youtube
        profile_form.mixer.data = current_user.mixer
        profile_form.r6_user.data = current_user.r6_user
        profile_form.platform.data = current_user.platform.name
    return render_template('edit_profile.html', title='Edit Profile',
                           profile_form=profile_form, pass_form=pass_form, del_form=del_form)


@app.route('/edit_profile/update_password', methods=['GET', 'POST'])
@login_required
def update_password():
    if current_user.is_authenticated:
        form = PasswordChangeForm(current_user)
        if form.validate_on_submit():
            current_user.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
            logout()
            return redirect(url_for('login'))
        return jsonify({'old_pass_error': form.original_password.errors,
                        'new_pass1_error': form.password.errors,
                        'new_pass2_error': form.password2.errors})