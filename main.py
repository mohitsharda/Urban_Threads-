from flask import *
import datetime


webApp = Flask("Urban Threads")

@webApp.route("/") #Decorator
def index():
    return render_template("index.html") # it is used to return webpages

@webApp.route("/register") 
def register():
    return render_template("register.html") 

def main():
    webApp.run() #it will run the app infinitely till user wont quite

if __name__ ==  "__main__":
    main()