from flask import *
import datetime
import hashlib
from database import MongoDbHelper
import os
from werkzeug.utils import secure_filename

webApp = Flask("Urban Threads And Accessories")
dbHelper = MongoDbHelper()

# Predefined admin credentials (hardcoded)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '54321'  # Hash the password in production (this is just an example)

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
        session['phoneNumber'] = loginData["phoneNumber"]
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
    session['phoneNumber'] = registerData["phoneNumber"]  # Store phone number in session

    return render_template("index.html", email=session['email'])

#handle to add product on backen
# Add product route
@webApp.route("/addProduct", methods=["POST"])
def addProduct():
    # Handle image upload
    image = request.files.get("imageURL")  # Get the uploaded file
    
    if image:
        # Ensure the file is not empty and the filename is secure
        filename = secure_filename(image.filename)
        
        # Set the upload folder path
        upload_folder = os.path.join('static', 'uploads')
        
        # Check if the folder exists, if not, create it
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Create the complete file path where the image will be saved
        image_path = os.path.join(upload_folder, filename)
        
        # Save the image to the folder
        image.save(image_path)
        
        # Construct the image URL for accessing it in the browser (relative to the static folder)
        image_url = f"/static/uploads/{filename}"
    else:
        image_url = None  # If no image is uploaded, set the URL to None
    
    # Get other product data from the form
    productData = {
        "name": request.form["name"],
        "price": int(request.form["price"]),
        "imageURL": image_url,  # Store the image URL in the document
        "category": request.form["category"],
        "createdOn": datetime.datetime.now()
    }

    try:
        # Connect to the MongoDB collection and insert the product data
        dbHelper.collection = dbHelper.db["Products"]
        
        # Insert the product document, ensure dbHelper.insert() is correct
        result = dbHelper.insert(productData)
        
        if result is not None:
            print(f"New product added with ID: {result.inserted_id}")  # Log the insertion
            return redirect(url_for('shop'))  # Redirect to shop page after successful insertion
        else:
            return "Error: Product could not be added to the database."
    
    except Exception as e:
        print(f"Error adding product: {e}")
        return "Error: Something went wrong while adding the product."


@webApp.route("/register") 
def register():
    return render_template("register.html") 

@webApp.route("/homepage") 
def homepage():
    return render_template("homepage.html") 

# @webApp.route("/shop")   
# def shop():
#     return render_template("shop.html") 

# Fetch all products for the shop page
@webApp.route("/shop")
def shop():
    dbHelper.collection = dbHelper.db["Products"]
    products = dbHelper.fetch()  # Fetch all products
    return render_template("shop.html", products=products)



@webApp.route("/cart") 
def cart():
    return render_template("cart.html") 

@webApp.route("/adminLogin", methods=["GET", "POST"])
def adminLogin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the credentials match
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True  # Set session for admin login
            return redirect(url_for("admin"))  # Redirect to the admin dashboard
        else:
            return render_template("adminlogin.html", error="Invalid credentials. Please try again.")  # Error message
    
    return render_template("adminlogin.html")  # Display login page if no POST request


@webApp.route("/admin")
def admin():
    # Check if the admin is logged in
    if not session.get("is_admin"):
        return redirect(url_for("adminLogin"))  # Redirect to login if not logged in
    
    # Render the admin dashboard
    response = render_template("admin.html")
    
    # Immediately log out the admin by clearing the session
    session.pop("is_admin", None)
    
    return response

@webApp.route("/userprofile")
def userProfile():
    # Print session details to debug
    print("Session Data:", session)

    name = session.get("name", "Guest")
    email = session.get("email", "Not provided")
    phone_number = session.get("phoneNumber", "Not provided")
    
    return render_template("userprofile.html", name=name, email=email, phone_number=phone_number)



def main():
    #In order to using sessions tracking ,, create a secret key
    webApp.secret_key = "What are you looking go and shop"

    webApp.run() #it will run the app infinitely till user wont quite
    #webApp.run(port=5001) optionally you can give the port number

if __name__ ==  "__main__":
    main()