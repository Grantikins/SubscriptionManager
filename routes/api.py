from flask import Blueprint, request, jsonify
from models.models import User, Subscription
import calendar

apiRoutes = Blueprint("routes", __name__)

@apiRoutes.route("/api/user/<userid>/")
def getUser(userid: int):
    return jsonify(User.query.filter_by(id=userid).first().json())

@apiRoutes.route("/api/subscription/<subid>/")
def getSubscription(subid: int):
    return jsonify(Subscription.query.filter_by(id=subid).first().json())

@apiRoutes.route("/api/subscription/<subid>/payment-days-in-month/<year>/<month>")
def getPaymentDays(subid: int, year: int, month: int):
    return jsonify(Subscription.query.filter_by(id=subid).first().getPaymentDaysinMonth(int(year), int(month)))

@apiRoutes.route("/api/subscription/<year>/<month>")
def getMonthDays(year: int, month: int):
    dayList = []
    for day in calendar.Calendar(firstweekday=calendar.SUNDAY).itermonthdates(int(year), int(month)):
        dayList.append(day)
    return jsonify(dayList)
    
@apiRoutes.route("/api/subscription/<subid>/is-payment-day/<year>/<month>/<day>")
def getIsPaymentDay(subid: int, year: int, month: int, day: int):
    return jsonify(Subscription.query.filter_by(id=subid).first().getIsPaymentDay(year, month, day))