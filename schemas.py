noteSchema = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "description", "tag"],
        "properties": {
            "title": {
                "bsonType": "string",
                "description": "Title of the note being added"
            },
            "description": {
                "bsonType": "string",
                "description": "Description of the note being added",
            },
            "tag": {
                "bsonType": "string",
                "description": "Tag for the category the note belongs to"

            },
            "email": {
                "bsonType": "string",
            },
        }
    }
}

userSchema = {
    "$jsonSchema":{
        "bsonType":"object",
        "required":["name","email","password"],
        "properties":
        {
            "name":{
                "bsonType":"string",
                "description":"Name of the user the is being added !"
            },
            "email":{
                "bsonType":"string",
                "description":"The email of the user being added!"
            },
            "password":{
                "description":"Password for the email that the user has provided !"
            }
        }
    }
}