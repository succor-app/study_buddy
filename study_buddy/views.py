from study_buddy import app, mongo_db
from forms import RegistrationForm, LoginForm, GroupForm
from helpers import *

from flask import url_for, redirect, session, render_template, request, flash
from pymongo import ASCENDING, DESCENDING
from mongokit import ObjectId
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from flask.ext.login import login_required, login_user, logout_user, current_user
from flask.ext.wtf import Form


# @app.route('/login', methods=["GET", "POST"])
# def login():
#     form = LoginForm(request.form)
#     if form.validate_on_submit():
#         print "form validated"
#         login_user(form.get_user(), remember=form.remember.data) # login_user(user, remember=True)
#         flash("Logged in succesfully")
#         return redirect(request.args.get("next") or url_for('home'))
#     return render_template('login.html', form=form)

@app.route('/user', defaults={'user_id' : None})
@app.route('/user/<user_id>', methods=["GET", "POST"])
#@login_required
def user(user_id):
    if user_id is None:
        user = current_user
    else:
        user = mongo_db.users.User.find_one({'_id' : ObjectId(user_id)})

    if request.method == "POST":
        # /user/<user_id>?new_class=<class name>
        if 'new_class' in request.args:
            old_classes = user.classes
            old_classes.append(request.args.get('new_class'))
            user.classes = old_classes
            if user.save():
                return 'success!'
            else:
                return "didn't work"
    else:
        if user_id is None:
            return render_template('profile.html', user=current_user)      
        else:
            user = mongo_db.users.User.find_one({'_id' : ObjectId(user_id)})
            return render_template('profile.html', user=user)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm(request.form)
#     if form.validate_on_submit():
#         # Create user
#         user_email = form.email.data
#         password = form.password.data

#         if mongo_db.users.User.find({'email' : user_email}).count() > 0:
#             flash('An account with that email already exists!')
#             form = RegistrationForm()
#             return render_template('register.html', form=form)
#         else:
#             new_user = mongo_db.users.User()
#             new_user.email = user_email
#             new_user.password = generate_password_hash(password)
#             new_user.save()

#         # log user in
#         login_user(new_user)
#         return redirect(url_for('home'))
#     if 'user_email' in session:
#         return render_template('register.html', email=session['user_email'], form=form)
#     else:
#         return render_template('register.html', form=form)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/group/<group_id>")
def group(group_id):
    group = mongo_db.study_sessions.StudySession.find_one({'_id' : ObjectId(group_id)})
    return render_template('group.html', group=group)

@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/find")
def search():

    if 'new_find' in request.args: # request coming from /find page
        search_query = request.args.get('new_find').lower()
        dept_keyword, course_keyword = parse_new_find(search_query)
    else:
        course_keyword = request.args.get('course_no')
        dept_keyword = request.args.get('dept_keyword').lower()

    print "DEPT KEYWORD:",dept_keyword
    print "COURSE KEYWORD:",course_keyword

    search_results = None
    results_exist = True

    date_now = datetime.today() - timedelta(hours=1)
    if course_keyword and dept_keyword:
        upcoming_search_results = mongo_db.study_sessions.StudySession.find(
            {'course_no' : course_keyword, 
             'department' : dept_keyword,  
             'time' : {'$gte' : date_now}})
        old_search_results = mongo_db.study_sessions.StudySession.find(
            {'course_no' : course_keyword, 
             'department' : dept_keyword,  
             'time' : {'$lt' : date_now}})
    elif dept_keyword and not course_keyword:
        print "only department entered"
        upcoming_search_results = mongo_db.study_sessions.StudySession.find(
            {'department' : dept_keyword,
             'time' : {'$gte' : date_now}})
        old_search_results = mongo_db.study_sessions.StudySession.find(
            {'department' : dept_keyword,
             'time' : {'$lt' : date_now}})
    elif not dept_keyword and not course_keyword:
        upcoming_search_results = mongo_db.study_sessions.StudySession.find(
            {'time' : {'$gte' : date_now}})
        old_search_results = mongo_db.study_sessions.StudySession.find(
            {'time' : {'$lt' : date_now}})
    else:
        flash('Enter something to search!')
        return render_template('index.html')
    
    upcoming_search_results.sort('time', ASCENDING)
    old_search_results.sort('time', DESCENDING)

    upcoming_search_results.rewind()
    return render_template('search_results.html', 
        upcoming_results = upcoming_search_results,
        old_results = old_search_results, 
        results_exist = (upcoming_search_results.count() > 0 or old_search_results > 0))


# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('home'))

@app.route('/create', methods=["POST","GET"])
def create():
    create_form = GroupForm(request.form)
    if create_form.validate_on_submit():
        new_session=mongo_db.study_sessions.StudySession()
        # store department as lower case so search works
        new_session.department=create_form.department.data.lower() 
        new_session.course_no=str(create_form.course_no.data)
        new_session.time=create_form.datetime.data
        new_session.location=create_form.where.data
        new_session.description=create_form.assignment.data
        new_session.contact_info=create_form.email.data
        new_session.details=create_form.details.data
        new_session.name=create_form.name.data
        new_session.save()
        flash("Group Created!")
        return redirect(url_for('group', group_id=new_session._id))
    return render_template('create.html',username='dummy', form=create_form);
    #return render_template('create.html',username=session['username']);

# ##
# # Responds to route /lucky, returning a random group study session from database.
# ##
# @app.route('/lucky')
# def lucky():
#     number_of_records = db.group_sessions.count()
#     random_number = random.randint(0,number_of_records-1)
#     group_session = db.group_sessions.find().limit(-1).skip(random_number).next()
#     return 'picked random session with id: ' + str(group_session['_id'])

##
# Responds to a url of the form: 
#   /edit?department=<department>&course_no=<course_no>&location=<location>&time=<time>&attendees=<attendees>&course_notes=<course_notes>&group_id=<group_id>
#   
#   department : string
#   course_no : string
#   location : string
#   time : string
#   attendees : list of strings
#   course_notes : string
#   group_id : string
##
# @app.route('/edit',methods=['POST'])
# def edit():
#     department = request.args.get('department')
#     course_no = request.args.get('course_no')
#     location = request.args.get('location')
#     time = request.args.get('time')
#     attendees = request.args.get('attendees')
#     course_notes = request.args.get('course_notes')
#     group_id = request.args.get('group_id')

#     coll = db.group_sessions
#     new_data = {DEPARTMENT_KEY    : department,
#                 COURSE_NUMBER_KEY : course_no,
#                 LOCATION_KEY      : location,
#                 TIME_KEY          : time,
#                 ATTENDEES_KEY     : attendees,
#                 COURSE_NOTES_KEY  : course_notes}

#     # verify that user owns the group before updating database.
#     coll.update({'_id' : group_id}, new_data)

#     # Show the updated results page.


# @app.route('/delete',methods=['POST'])
# def delete():
#     # TODO: verify that user in session owns the group session to be deleted
#     pass

##
# Add the current user to the selected study session group.
# Responds to route of the form:
#   /join?group_id=<group_id>
#   
#   group_id : string
##
# @app.route('/join',methods=['POST'])
# def join():
#     user = db.users.find_one({"userID": session['userid']})
#     group_id = request.args.get('group_id')
#     db_results_list = cursortolst(db.group_sessions.find())

#     insert_item = {}
    
#     for item in db_results_list:
#         print str(item['_id']) + " =? " + str(group_id)
#         if str(group_id) == str(item['_id']):
#             print "we have a match!"
#             item[ATTENDEES_KEY].append([user['userID'], user['name']])
#             insert_item = item
#     # current_study_group = db.group_sessions.find_one({'_id': group_id})
#     print insert_item
#     # Check that user is in the attendees of current_study_group
#     # if user in usercurrent_study_group.attendees:
#         # Show user that he/she is already in the group.

#     coll = db.group_sessions
#     #new_attendees_list = current_study_group[ATTENDEES_KEY].add(user)
#     coll.update({'_id': insert_item['_id']}, insert_item, True)
#     print list(coll.find())
#     # Return that the database was updated and refresh the page with new attendees list.
#     return 'success'









