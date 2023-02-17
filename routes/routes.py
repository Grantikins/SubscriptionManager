from flask import render_template, Blueprint, redirect, request, session, flash, url_for
from flask_login import login_user, current_user, logout_user, login_required
from models.models import db, User, Subscription
from datetime import datetime, timedelta
import calendar
from flask_bcrypt import Bcrypt

routes = Blueprint("routes", __name__)
bcrypt = Bcrypt()

@routes.route('/')
@login_required
def home():
    activeSubscriptions, inactiveSubscriptions, subDates = [], [], []
    subscriptions, subValue = Subscription.query.filter_by(user_id=session["id"]).all(), 0
    for sub in subscriptions:
        sub.setNextPaymentDate()
        db.session.commit()
        if sub.active:
            subValue += sub.paymentAmount
            activeSubscriptions.append(sub)
        else:
            inactiveSubscriptions.append(sub)
        subDates.append( (sub.json(), sub.getPaymentDaysinMonth(datetime.now().year, datetime.now().month)) )
    
    dayList = []
    for day in calendar.Calendar(firstweekday=calendar.SUNDAY).itermonthdates(datetime.now().year, datetime.now().month):
        dayList.append(day)
    
    currDay1, currDay2, upcoming, pastSpent = datetime.now(), datetime.now(), 0, 0
    for i in range(30):
        for sub in subscriptions:
            if sub.getIsPaymentDay(currDay1.year, currDay1.month, currDay1.day):
                upcoming += sub.paymentAmount
            if sub.getIsPaymentDay(currDay2.year, currDay2.month, currDay2.day):
                pastSpent += sub.paymentAmount
        currDay1 += timedelta(days=1)
        currDay2 -= timedelta(days=1)

    return render_template("home.html", aSubs=activeSubscriptions, iSubs=inactiveSubscriptions, name=session["name"], date=datetime.now(), dayList=dayList, subDates=subDates, user_id=session["id"], subValue=subValue, upcoming=upcoming, pastSpent=pastSpent)

@routes.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        try:
            user = User.query.filter_by(email=request.form["email"]).first()
            if not user:
                raise ValueError("There is no account associated with that email address.")
            if not bcrypt.check_password_hash(user.password, request.form["password"]):
                raise ValueError("Incorrect password")
            session["id"] = user.id
            session["name"] = user.name
            session["email"] = user.email
            session["passwordLength"] = len(request.form["password"])
            login_user(user)
        except ValueError as e:
            flash(str(e), "error")
            return redirect("/login")
        return redirect("/")
    
    return render_template("login-signup.html")

@routes.route("/signup/", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        try:
            if User.query.filter_by(email=request.form["email"]).first():
                raise ValueError("That email is already in use. You may have an account already.")
            if len(request.form["email"]) == 0 or len(request.form["name"]) == 0:
                raise ValueError("You need to provide a name and a password.")
            
            passvalue = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
            user = User(request.form["name"], request.form["email"], passvalue)
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            flash(str(e), "error")
            return redirect("/login")
        flash("You have successfully made an account!", "success")
        return redirect("/login")
    
    return redirect("/login")

@routes.route("/addsubscription/", methods=["GET", "POST"]) 
@login_required
def addSubscription():
    if request.method == "POST":
        try:
            if len(request.form["serviceName"]) == 0 or len(request.form["paymentAmount"]) == 0:
                raise ValueError("You need to enter a service name and payment amount.")
            
            interval, startDate, url = None, None, None
            if len(request.form["startDate"]) != 0:
                date = request.form["startDate"].split("-")
                startDate = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2])) 
            if len(request.form["subURL"]) != 0: 
                url = request.form["subURL"]
            if len(request.form["intervalUnit"]) != 0 and len(request.form["intervalNum"]) != 0:
                interval = str(request.form["intervalNum"]) + " " + request.form["intervalUnit"]
            
            active = False
            try:
                if request.form["active"]:
                    active = True
            except Exception as e:
                pass
            
            sub = Subscription(request.form["serviceName"], request.form["paymentAmount"], session["id"], startDate, interval, url, active)
            db.session.add(sub)
            db.session.commit()
            
            flash("Successfully added subscription!", "success")
            return redirect("/addsubscription")
        except ValueError as e:
            flash(str(e), "error")
            return redirect("/addsubscription")
    
    return render_template("addsubscription.html")

@routes.route("/account/", methods=["GET", "POST"])
@login_required
def account():
    if request.method == "POST":
        try:
            user = User.query.filter_by(id=session["id"]).first()
            for key in request.form:
                if len(request.form[key]) == 0: 
                    raise ValueError("You must provide a value with at least one character.")
                match key:
                    case "nameValue": 
                        user.name = request.form[key]
                        session["name"] = user.name
                    case "emailValue": 
                        user.email = request.form[key]
                        session["email"] = user.email
                    case "passwordValue": 
                        user.password = bcrypt.generate_password_hash(request.form[key])
                        session["passwordLength"] = len(request.form[key])
            db.session.commit()
        except (KeyError, ValueError) as e:
            flash(str(e), "error")
        
        redirect("/account")
    return render_template("account.html", name=session["name"], email=session["email"], password="*"*session["passwordLength"])

@routes.route("/subscription/<subid>/")
@login_required
def getSubscription(subid: int):
    sub = Subscription.query.filter_by(id=subid).first()
    sub.setNextPaymentDate()
    db.session.commit()
    return render_template("subscription.html", sub=Subscription.query.filter_by(id=subid).first())

@routes.route("/subscription/<subid>/deactivate/", methods=["GET", "POST"])
@login_required
def deactivateSubscription(subid: int):
    sub = Subscription.query.filter_by(id=subid).first()
    sub.active = False
    db.session.commit()
    flash("Subscription deactivation successful!", "success")
    return redirect(f"/subscription/{subid}", "success")

@routes.route("/subscription/<subid>/activate/", methods=["GET", "POST"])
@login_required
def activateSubscription(subid: int):
    sub = Subscription.query.filter_by(id=subid).first()
    sub.active = True
    db.session.commit()
    flash("Subscription activation successful!", "success")
    return redirect(f"/subscription/{subid}", "success")

@routes.route("/subscription/<subid>/delete/", methods=["DELETE"])
@login_required
def deleteSubscription(subid: int):
    sub = Subscription.query.filter_by(id=subid).first()
    db.session.delete(sub)
    db.session.commit()
    return redirect("/", "success")

@routes.route("/subscription/<subid>/edit/", methods=["GET", "POST"])
@login_required
def editSubscription(subid: int):
    sub = Subscription.query.filter_by(id=subid).first()
    print(request.method)
    if request.method == "POST":
        try:
            if len(request.form["serviceName"]) == 0 or len(request.form["paymentAmount"]) == 0:
                raise ValueError("You need to enter a service name and payment amount.")
            
            interval, startDate, url = None, None, None
            if len(request.form["startDate"]) != 0:
                date = request.form["startDate"].split("-")
                startDate = datetime(year=int(date[0]), month=int(date[1]), day=int(date[2])) 
            if len(request.form["subURL"]) != 0: 
                url = request.form["subURL"]
            if len(request.form["intervalUnit"]) != 0 and len(request.form["intervalNum"]) != 0:
                interval = str(request.form["intervalNum"]) + " " + request.form["intervalUnit"]
            
            active = False
            try:
                if request.form["active"]:
                    active = True
            except Exception as e:
                pass
            
            sub.serviceName = request.form["serviceName"]
            sub.paymentAmount = request.form["paymentAmount"]
            sub.timeBetweenPayments = interval
            sub.startDate = startDate
            sub.urlAssociated = url
            sub.active = active
            db.session.commit()
            print("here")
            
            flash("Subscription changes made!", "success")
            return redirect(f"/subscription/{subid}/edit")
        except ValueError as e:
            flash(str(e), "error")
            return redirect(f"/subscription/{subid}/edit") 
    print("here2")     
    return render_template("editsubscription.html", sub=sub)

@routes.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect("/login")


