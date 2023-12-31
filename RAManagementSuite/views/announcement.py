from flask import Flask, Blueprint, render_template, request, url_for, flash, redirect, jsonify, abort
from flask_login import login_required, current_user

from models import Event, UserRole, TaskPriority, User, TaskStatus, EventType
from repos import announcementRepo, taskRepo

announcement = Blueprint('announcement', __name__)


@announcement.route('/')
@login_required
def index():
    current_page = 'index'
    announcements = announcementRepo.get_announcements()
    return render_template('announcement/index.html', announcements=announcements, current_page=current_page, UserRole=UserRole)


@announcement.route('/view/<int:announcement_id>')
@login_required
def view(announcement_id):
    current_page = 'view'
    announcement = announcementRepo.get_announcement(announcement_id)
    return render_template('announcement/view.html', announcement=announcement, UserRole=UserRole, current_page=current_page)


@announcement.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if current_user.role == UserRole.BASIC:
        flash('You do not have permission to create announcements.')
        return redirect(url_for('announcement.index'))

    current_page = 'create'
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            announcementRepo.create_announcement(title, content, current_user.id)
            return redirect(url_for('announcement.index'))

    return render_template('announcement/create.html', current_page=current_page)


@announcement.route('/edit/<int:announcement_id>/', methods=('GET', 'POST'))
@login_required
def edit(announcement_id):
    if current_user.role == UserRole.BASIC:
        flash('You do not have permission to create announcement.')
        return redirect(url_for('announcement.index'))

    current_page = 'edit'
    announcement = announcementRepo.get_announcement(announcement_id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            announcementRepo.edit_announcement(title, content, announcement_id)
            return redirect(url_for('announcement.index'))

    return render_template('announcement/edit.html', announcement=announcement, current_page=current_page)


@announcement.route('/delete/<int:announcement_id>/')
@login_required
def delete(announcement_id):
    if current_user.role == UserRole.BASIC:
        flash('You do not have permission to create announcements.')
        return redirect(url_for('announcement.index'))

    announcementRepo.del_announcement(announcement_id)
    return redirect(url_for('announcement.index'))

