from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_login import UserMixin
from sqlalchemy import Integer, String, Float, DateTime, Boolean
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta

db = SQLAlchemy()
loginManager = LoginManager()

@loginManager.user_loader
def load_user(userID):
    return User.query.get(int(userID))

class Subscription(db.Model):                       
    id = db.Column(Integer(), primary_key=True)
    user_id = db.Column(Integer(), db.ForeignKey("user.id"), nullable=False)
    serviceName = db.Column(String(80), nullable=False)
    paymentAmount = db.Column(Float(), nullable=False)
    startDate = db.Column(DateTime())
    timeBetweenPayments = db.Column(String(20))
    nextPaymentDate = db.Column(DateTime())
    urlAssociated = db.Column(String(30))
    active = db.Column(Boolean())
    totalSpent = db.Column(Float())
    
    def __init__(self, serviceName: str, paymentAmount: float, user_id: int, startDate: datetime=None, timeBetween: str=None, urlAssociated: str=None, active: bool=True):
        self.serviceName = serviceName
        self.paymentAmount = paymentAmount
        self.startDate = startDate
        if timeBetween and startDate and len(timeBetween.split(" ")) == 2:
            self.timeBetweenPayments = timeBetween
            self.setNextPaymentDate()
        else:
            self.timeBetweenPayments = timeBetween
            self.nextPaymentDate = None
            self.totalSpent = None
        self.user_id = user_id
        self.urlAssociated = urlAssociated
        self.active = active
        
    def setNextPaymentDate(self):
        if self.timeBetweenPayments and self.startDate and len(self.timeBetweenPayments.split(" ")) == 2:
            number, unit = self.timeBetweenPayments.split(" ")[0], self.timeBetweenPayments.split(" ")[1]
            self.nextPaymentDate = datetime.now()
            count = 0
            while self.nextPaymentDate <= datetime.now():
                match unit:
                    case "Month(s)": self.nextPaymentDate = self.startDate + relativedelta(months=count*int(number))
                    case "Week(s)": self.nextPaymentDate = self.startDate + relativedelta(weeks=count*int(number))
                    case "Day(s)": self.nextPaymentDate = self.startDate + relativedelta(days=count*int(number))
                    case "Year(s)": self.nextPaymentDate = self.startDate + relativedelta(years=count*int(number))
                count += 1
            self.totalSpent = (count - 1) * self.paymentAmount
    
    def json(self):
        return {
            "id": self.id,
            "serviceName": self.serviceName,
            "paymentAmount": self.paymentAmount,
            "startDate": self.startDate,
            "timeBetweenPayments": self.timeBetweenPayments,
            "nextPaymentDate": self.nextPaymentDate,
            "totalSpent": self.totalSpent,
            "urlAssociated": self.urlAssociated,
            "active": self.active,
            "userID": self.user_id
        }
    
    def getPaymentDaysinMonth(self, year: int, month: int):
        givenDate = datetime(year, month, calendar.monthrange(year, month)[1])
        if self.timeBetweenPayments and self.startDate and len(self.timeBetweenPayments.split(" ")) == 2 and self.startDate <= givenDate and self.active:
            subDates = []
            number, unit = self.timeBetweenPayments.split(" ")[0], self.timeBetweenPayments.split(" ")[1]
            match unit:
                case "Month(s)": interval = relativedelta(months=int(number))
                case "Week(s)": interval = relativedelta(weeks=int(number))
                case "Day(s)": interval = relativedelta(days=int(number))
                case "Year(s)": interval = relativedelta(years=int(number))
           
            currDate = self.startDate
            while currDate <= givenDate:
                if currDate.month == month and currDate.year == year:
                    subDates.append(currDate.date())
                currDate += interval
            
            return subDates
    
    def getIsPaymentDay(self, year: int, month: int, day: int):
        givenDate = datetime(year, month, day)
        if self.timeBetweenPayments and self.startDate and len(self.timeBetweenPayments.split(" ")) == 2 and self.startDate <= givenDate and self.active:
            number, unit = self.timeBetweenPayments.split(" ")[0], self.timeBetweenPayments.split(" ")[1]
            match unit:
                case "Month(s)": interval = relativedelta(months=int(number))
                case "Week(s)": interval = relativedelta(weeks=int(number))
                case "Day(s)": interval = relativedelta(days=int(number))
                case "Year(s)": interval = relativedelta(years=int(number))
            
            currDate = self.startDate
            while currDate <= givenDate:
                if currDate.date() == givenDate.date():
                    return True
                currDate += interval
                
        return False
    
    def __repr__(self):
        return f"Subscription for {self.serviceName} owned by id: {self.user_id}"
    
    
class User(db.Model, UserMixin):
    id = db.Column(Integer(), primary_key=True)
    name = db.Column(String(80), nullable=False)
    email = db.Column(String(120), nullable=False, unique=True)
    password = db.Column(String(80), nullable=False)
    subscriptions = db.relationship("Subscription", backref="subscriber", lazy=True)
    
    def __init__(self, name: str, email: str, password: str):
        self.name = name
        self.email = email
        self.password = password
        
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "subscriptions": [sub.json() for sub in self.subscriptions]
        }
    
    def __repr__(self):
        return f"name: {self.name}; email: {self.email}; password: {self.password}"
    