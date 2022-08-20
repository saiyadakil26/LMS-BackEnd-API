from flask import Flask , make_response,jsonify,request,render_template
from flask_mongoengine import MongoEngine
import pymongo
from bson.json_util import dumps
import json
from datetime import datetime

app = Flask(__name__)
connection_url ="mongodb+srv://pratik:pratik123@cluster0.jf2ec.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
app = Flask(__name__)
client = pymongo.MongoClient(connection_url)
# Database
Database = client.get_database('Library')
# Table
SampleTable = Database.BOOKS

#home page endpoint
@app.route('/',methods =['GET'])
def Home():
    return render_template('overview.html')

"""                
@app.route('/api/db_pop',methods =['POST'])
def db_pop():
    SampleTable = Database.BOOKS
    body = request.get_json()
    query = SampleTable.insert_one(body)
    return str(query)
"""

@app.route('/api/get_name/<name>',methods =['GET'])
def get_name(name):
    SampleTable = Database.BOOKS
    query =list(SampleTable.find( {"book_name": {"$regex": name, "$options": "i"} }))
    return str(query)

@app.route('/api/get_rent/<minR>/<maxR>',methods =['GET'])
def get_rent(minR,maxR):
    SampleTable = Database.BOOKS
    query =list(SampleTable.find( {"rent_per_day":{ '$gt':int(minR), '$lt':int(maxR)}}))
    return str(query)


@app.route('/api/get_list/<name>/<cat>/<rent>',methods =['GET'])
def get_list(name,cat,rent):
    SampleTable = Database.BOOKS
    query =list(SampleTable.find( {"book_name": {"$regex": name, "$options": "i"}, "category":cat ,"rent_per_day":int(rent) }))
    return str(query)



@app.route('/api/book_issue/',methods =['POST'])
def book_issue():
    SampleTable = Database.TRANSACTIONS
    body = request.get_json()
    query = SampleTable.insert_one(body)
    return str(body)

@app.route('/api/book_return/',methods =['POST'])
def book_return():
    SampleTable = Database.TRANSACTIONS
    body = request.get_json()
    date_str=body.get("return_date")
    b_name = body.get("book_name")
    p_name = body.get("person_name")
    res = list(SampleTable.find({"book_name":b_name,"person_name":p_name},{"_id":0,"book_name":0,"person_name":0}))
    
    F_date=res[0].get("issue_date")
    L_date=date_str
    
    d1 = datetime.strptime(F_date, "%Y/%m/%d")
    d2 = datetime.strptime(L_date, "%Y/%m/%d")
    
    total= d2-d1
    day = total.days

    SampleTable = Database.BOOKS
    myrent = list(SampleTable.find({"book_name":b_name},{"_id":0,"book_name":0,"category":0}))
    rent = int(myrent[0].get("rent_per_day"))*day

    SampleTable = Database.TRANSACTIONS
    
    query = SampleTable.update_one({"book_name":b_name,"person_name":p_name},{ "$set":{ "return_date" :date_str,"rent":rent}})
    return str(body)

@app.route('/api/people_list/<name>/',methods =['GET'])
def people_list(name):
    SampleTable = Database.TRANSACTIONS
    query=list(SampleTable.find({"book_name":name,"return_date": { "$exists": "true", "$ne": "null" } }))
    return str(query)


@app.route('/api/total_rent/<name>/',methods =['GET'])
def total_rent(name):
    SampleTable = Database.TRANSACTIONS
    query=list(SampleTable.find({"book_name":name},{"_id":0,"rent":1}))
    rent=0;
    for i in  range(0,len(query)):
        rent+=query[i].get("rent")
    return str(rent)

@app.route('/api/booklist_peron/<name>/',methods =['GET'])
def booklist_peron(name):
    SampleTable = Database.TRANSACTIONS
    query=list(SampleTable.find({"person_name":name},{"_id":0,"book_name":1}))
    return str(query)

@app.route('/api/date_range/<mindate>/<maxdate>',methods =['GET'])
def date_range(mindate,maxdate):
    SampleTable = Database.TRANSACTIONS
    d1 = datetime.strptime(mindate, "%Y-%m-%d")
    d2 = datetime.strptime(maxdate, "%Y-%m-%d")
    query=list(SampleTable.find())
    ls=[]
    for i in  range(0,len(query)):
        c = datetime.strptime(query[i].get("issue_date"), "%Y/%m/%d")
        if d1<c<d2:
              ls.append(query[i].get("person_name"))
    return str(ls)


if __name__ == '__main__':
    app.run()