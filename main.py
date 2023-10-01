from schemas import userSchema, noteSchema
from flask import Flask,request,jsonify
from bson import ObjectId
import pymongo
import bcrypt,jwt

jwtSecretKey="dianadoodle"
client = pymongo.MongoClient("mongodb://127.0.0.1:27017")
database= client["iNotebook2"]

collectionList= database.list_collection_names()

checkUsers= "users" in collectionList
checkNotes= "notes" in collectionList

if (checkUsers==False):
    collectionUser= database.create_collection("users",validator=userSchema)
    collectionUser.create_index([('email',1)],unique=True)

if (checkNotes == False):
    collectionNotes= database.create_collection("notes",validator=noteSchema)

#Starting the list of routes
app=Flask(__name__)
userCollection=database["users"]
noteCollection=database["notes"]
print(">>>>>>>>>>>>>Hello from iNotebook ! <<<<<<<<<<<<<")
#Route for user profile creation
@app.route("/createuser",methods=["POST"])
def login():
    try:
        data = request.get_json()
        print("data received:---------------- ",data)
        salt = bcrypt.gensalt(10)
        encrypedPassword= bcrypt.hashpw(data["password"].encode('utf-8'),salt)
        dataToAdd= {
            "name":data["name"],
            "email":data["email"],
            "password":encrypedPassword.decode('utf-8')
        }
        dataToSendInAuthToken= {
            "name":data["name"],
            "email":data["email"]
        }
        authToken=jwt.encode(dataToSendInAuthToken,jwtSecretKey)
        saveToDb= userCollection.insert_one(dataToAdd)
        if saveToDb.acknowledged == True:
            return "User created successfully !: "+authToken,200
        else:
            return "error in creating user with the details you have provided !",400
    except Exception as e:
        print(dir(e))
        return e.details,400
    

#Route for login in user after verifying the AuthToken:
@app.route("/loginuser",methods=["POST"])
def loginUser():
    try:
        data=request.get_json()
        userEmail=data["email"]
        password=data["password"]
        findEmailInDb= userCollection.find_one({"email":userEmail})
        checkPasswords= bcrypt.checkpw(password.encode('utf-8'),findEmailInDb["password"].encode('utf-8'))
        if (checkPasswords == True):
            authToken= jwt.encode({"name":findEmailInDb["name"],"email":findEmailInDb["email"]},jwtSecretKey)
            return "successful login :"+authToken,200
        else:
            return "login failed, please try again!",400
    except Exception as e:
        return e.details,400

#Route to get the loggedIn user details:
@app.route("/getuser",methods=["POST"])
def getuser():
    try:
        authToken= request.headers.get("auth-token")
        decodeToken= jwt.decode(authToken,jwtSecretKey,algorithms=["HS256"])
        if (decodeToken != jwt.ExpiredSignatureError or jwt.InvalidTokenError):
            print("Token verified succesfully!")
            return decodeToken
        else:
            print("Token verification failed!")
            print("null")
            return None
    except Exception as e:
        return None

#Route to add a new note for a user:
@app.route("/addnote",methods=["POST"])
def addnote():
    try:
        getUser=getuser()
        if (getUser == None):
            return "Invalid Token detected!"
        else:
            print("Adding note to the database!")
            data = request.get_json()
            userEmail= getUser["email"]
            addingNote= noteCollection.insert_one({"title":data["title"],"description":data["description"],"tag":data["tag"],"email":userEmail})
            if (addingNote.acknowledged== True):
                return "Note added successfully !"
            else:
                return "Failed to add the note!"
    except Exception as e:
        return e

#Fetching all the notes for a specific user from the database:
@app.route("/fetchallnotes",methods=["GET"])
def fetchallnotes():
    getUser=getuser()
    if (getUser==None):
        return "Invalid token detected !"
    else:
        print("fetching notes for user :", getUser["name"])
        userEmail= getUser["email"]
        fetchNotes= noteCollection.find({"email":userEmail})
        dataFetched=[]
        for i in fetchNotes:
            dataToAppend={"title":i["title"],"description":i["description"],"tag":i["tag"]}
            dataFetched.append(dataToAppend)
        return dataFetched
    
#Deleting an existing note in the database for a user
@app.route("/deletenote/<id>",methods=["DELETE"])
def deletenote(id):
    try:
        getUser=getuser()
        if (getUser==None):
            return "Invalid token detected !"
        else:
            getIdDetails= noteCollection.find_one({"_id":ObjectId(id)})
            if (getIdDetails==None):
                return "No note found with the ID provided!"
            else:
                print (getIdDetails)
                if (getIdDetails["email"]==getUser["email"]):
                    deletingNote= noteCollection.find_one_and_delete({"_id":ObjectId(id)})
                    return "Note deleted successfully!"
                else:
                    return "This note doesn't belong to you!"
    except Exception as e:
        return dir(e)
    
#Updating an existing note in the database for a user
@app.route("/updatenote/<id>",methods=["POST"])
def updatenote(id):
    getUser=getuser()
    data= request.get_json()
    if (getUser== None):
        return "invalid token detected!"
    else:
        getIdDetails= noteCollection.find_one({"_id":ObjectId(id)})
        if (getUser["email"]== getIdDetails["email"]):
            dataToUpdate={
                "title":data["title"],
                "description":data["description"],
                "tag":data["tag"]
            }
            updatingData=noteCollection.find_one_and_update({"_id":ObjectId(id)},{'$set':dataToUpdate})
            if (updatingData==None):
                return "Error in upadting the data!",404
            else:
                return "Data upated Successfully !",200

        else:
            return "The note doesn't belong to you !",403


app.run(debug=True)

