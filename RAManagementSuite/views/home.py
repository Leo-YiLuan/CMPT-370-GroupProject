from flask import Flask, Blueprint, render_template, request, url_for, flash, redirect, jsonify
from flask_login import login_required, current_user

from models import Event
from repos import announcementRepo
from repos.eventRepo import create_event, get_all_events, update_event, delete_event
from models import ProfileForm

from RAManagementSuite.extensions import db

home = Blueprint('home', __name__)


@home.route('/')
def index():
    current_page = 'home'
    announcements = announcementRepo.get_announcements()
    return render_template('home/index.html', announcements=announcements, current_page=current_page)

@home.route('/announcement')
def announcement_page():
    current_page = 'announcement_page'
    announcements = announcementRepo.get_announcements()
    return render_template('home/announcement.html', announcements=announcements, current_page=current_page)

@home.route('/view/<int:announcement_id>')
def announcement(announcement_id):
    announcement = announcementRepo.get_announcement(announcement_id)
    return render_template('home/view.html', announcement=announcement)


@home.route('/create', methods=('GET', 'POST'))
def create():
    current_page = 'new_announcement'
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            announcementRepo.create_announcement(title, content)
            return redirect(url_for('home.announcement_page'))

    return render_template('home/create.html', current_page=current_page)


@home.route('/edit/<int:announcement_id>/', methods=('GET', 'POST'))
def edit(announcement_id):
    announcement = announcementRepo.get_announcement(announcement_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            announcementRepo.edit_announcement(title, content, announcement_id)
            return redirect(url_for('home.announcement_page'))

    return render_template('home/edit.html', announcement=announcement)

@home.route('/delete/<int:announcement_id>/')
def delete_announcement(announcement_id):
    announcementRepo.del_announcement(announcement_id)
    return redirect(url_for('home.announcement_page'))

# @home.route('/profile')
# @login_required
# def profile():
#     current_page = 'Profile'
#     return render_template('home/profile.html', name=current_user.name, current_page=current_page)
#

@home.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    # Fetch the user's profile from the database
    user_profile = ProfileForm.query.filter_by(user_id=current_user.id).first()
    if user_profile is None:
        user_profile = ProfileForm(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'POST':
        # Update the profile fields with form data
        user_profile.firstname = request.form.get('firstname')
        user_profile.lastname = request.form.get('lastname')
        user_profile.birthdate = request.form.get('birthdate')
        user_profile.phonenumber = request.form.get('phonenumber')
        user_profile.gender = request.form.get('gender')
        user_profile.pronouns = request.form.get('pronouns')
        user_profile.major = request.form.get('major')
        user_profile.addressline1 = request.form.get('addressline1')
        user_profile.addressline2 = request.form.get('addressline2')
        user_profile.postcode = request.form.get('postcode')
        user_profile.city = request.form.get('city')
        user_profile.province = request.form.get('province')
        user_profile.shift_availability = request.form.get('shift_availability')

        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('home.profile'))

    return render_template('home/profile.html', form=form, user_profile=user_profile)


@home.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    current_page = 'Calendar'
    if request.method == 'POST':
        # get data from form and create or update an event
        title = request.form.get('title')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        owner_id = current_user.id
        color = request.form.get('color')
        description = request.form.get('description')
        event_id = request.form.get('event_id')

        if event_id and event_id.strip() != '':  # If event_id is provided, it's an update
            update_event(event_id, title, start_date, end_date, color, description)
        else:  # Otherwise, it's a new event
            create_event(title, start_date, end_date, owner_id, color, description)
        return redirect(url_for('home.events'))

    events = get_all_events()
    return render_template('home/events.html', events=events, current_user=current_user, current_page=current_page)


@login_required
@home.route('/api/events', methods=['GET'])
def get_events():
    # Fetch events from your database
    events = Event.query.all()
    events_data = [{
        'id': event.id,
        'title': event.title,  # Combine event title with owner's name
        'start': event.start_date.isoformat(),
        'end': event.end_date.isoformat(),
        'color': event.color,
        'description': event.description,
        # 'url': url_for('home.events'),  # Pointing back to the main calendar
        'ownerId': event.owner_id
    } for event in events]

    return jsonify(events_data)


@home.route('/delete-event/<int:event_id>', methods=['POST'])
@login_required
def delete_event_route(event_id):
    event = Event.query.get(event_id)
    if event and event.owner_id == current_user.id:  # ensure the current user is the owner
        delete_event(event_id)
        return jsonify(success=True)
    return jsonify(success=False, message="Event not found or you don't have the permission to delete it")


user_data = {}

# @home.route('/submit_profile', methods=['POST'])
# def submit_profile():
#     if request.method == 'POST':
#         user_id = current_user.id  # Adjust this based on your authentication mechanism
#         user_data[user_id] = request.form.to_dict()
#
#     return redirect(url_for('profile'))