import os
from flask import Flask, request, render_template, redirect
from pymongo import MongoClient

MONGODB_URI = os.environ.get("MONGODB_URI")
MONGODB_NAME = os.environ.get("MONGODB_NAME")

app = Flask(__name__)

@app.route('/')
def get_index():
    return render_template('index.html')
    
@app.route("/login", methods=['POST'])
def do_login():
    username = request.form['username']
    return redirect(username)

@app.route("/<username>") 
def get_userpage(username):
    documents = load_documents(username)
    return render_template("user_home.html", username=username, documents=documents)

@app.route("/<username>/create_new_list", methods=["POST"]) 
def create_list(username):
    list_name= request.form['list_name']
    create_list_for_user(username,list_name)
    return redirect(username)
    
@app.route("/<username>/<list_name>/add_item", methods=["POST"]) 
def add_item_to_list(username, list_name):
    list_item= request.form['list_item']
    save_list_items_to_mongo(username, list_name, list_item)
    return redirect(username)
    

@app.route('/<username>/<list_name>/<item_name>/delete_item',methods=['POST'])
def delete_item(username, list_name, item_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        selected_list['list_items'].remove(item_name)
        db[username].save(selected_list)
        return redirect(username)
        
@app.route('/<username>/<list_name>/<item_name>/priority_item',methods=['POST'])
def priority_item(username, list_name, item_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        selected_list['list_items'].mark(item_name)
        db[username].save(selected_list)
        return redirect(username)

def create_list_for_user(username, list_name):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        db[username].insert({'name': list_name, 'list_items': [] })
        
# def load_lists_by_username(username):
#     with MongoClient(MONGODB_URI) as conn:
#         db = conn[MONGODB_NAME]
#         return db[username].find()

def save_list_items_to_mongo(username, list_name, new_list_item):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        selected_list = db[username].find_one({'name':list_name})
        selected_list['list_items'].append(new_list_item)
        db[username].save(selected_list)

def load_documents(username):
    with MongoClient(MONGODB_URI) as conn:
        db = conn[MONGODB_NAME]
        list_obj = db[username].find()
        return [l for l in list_obj]


if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)