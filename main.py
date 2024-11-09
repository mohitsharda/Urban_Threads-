from flask import *
import datetime
import hashlib
from database import MongoDbHelper

webApp = Flask("Urban Threads")
dbHelper = MongoDbHelper()

@webApp.route("/") #Decorator
def index():
    return render_template("index.html") # it is used to return webpages

@webApp.route("/fetchUser", methods=["POST"])
def fetchUserInDb():
    loginData = {
        "email" : request.form["email"],
        "passWord" : hashlib.sha256(request.form["passWord"].encode('utf-8')).hexdigest(),
    }

    # dbHelper.collection = dbHelper.db["Logins"]
    dbHelper.collection = dbHelper.db["Registers"]
    result = dbHelper.fetch(query = loginData)
    print("result : ", result)

    if len(result) > 0:
        loginData = result[0] # get the dictionary from the list
        session['email'] = loginData['email']  # Store the email in the session 
        session['name'] = loginData["name"]
        return render_template("homepage.html", name = session['name'], email = session['email'])
    else:
        return "User Not found: Please Try Again"
        
#in below function when user register then info. will be added in the mongodb
@webApp.route("/addUser", methods=["POST"])
def addUserInDb():
    registerData = {
        "name" : request.form["name"],
        "phoneNumber" : request.form["phoneNumber"],
        "email" : request.form["email"],
        "passWord" : hashlib.sha256(request.form["passWord"].encode('utf-8')).hexdigest(),
        "createdOn" : datetime.datetime.now()
    }

    dbHelper.collection = dbHelper.db["Registers"]
    result = dbHelper.insert(registerData)
    print(result)

    # session['userId'] = str(result.inserted_id)
    session['name'] = registerData["name"]
    session['email'] = registerData["email"]

    return render_template("index.html", email=session['email'])
    

@webApp.route("/register") 
def register():
    return render_template("register.html") 

@webApp.route("/homepage") 
def homepage():
    return render_template("homepage.html") 

@webApp.route("/shop") 
def shop():
    return render_template("shop.html") 

@webApp.route("/cart") 
def cart():
    return render_template("cart.html") 

def main():
    #In order to using sessions tracking ,, create a secret key
    webApp.secret_key = "What are you looking go and shop"

    webApp.run() #it will run the app infinitely till user wont quite
    #webApp.run(port=5001) optionally you can give the port number

if __name__ ==  "__main__":
    main()