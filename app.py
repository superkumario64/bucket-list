import logging
from flask import Flask, render_template, json, request, redirect, session
from flask.ext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
import uuid
import os

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'
mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'BucketList'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_PORT'] = 8889
app.config['UPLOAD_FOLDER'] = 'static/Uploads'
mysql.init_app(app)

# pagination limit
pageLimit = 2

#gereral fxn to call a sql stored procedure
def callProcedure(proc, dataTuple, isSelect):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.callproc(proc,dataTuple)
        data = cursor.fetchall()
        cursor.nextset()
        if isSelect:
            conn.commit()
            return data;
        else:
            if len(data) is 0:
                conn.commit()
                return data;
            else:
                return render_template('error.html',error = 'An error occurred!')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route("/")
def main():
    #If user is logged in redirect to dashboard
    #else render index
    if session.get('user'):
        return redirect('/showDashboard')
    else:
        return render_template('index.html')

@app.route('/addUpdateLike',methods=['POST'])
def addUpdateLike():
    if session.get('user'):
        _wishId = request.form['wish']
        _like = request.form['like']
        _user = session.get('user')
        data = callProcedure('sp_AddUpdateLikes',(_wishId,_user,_like),False)
        if len(data) is 0:
            result = callProcedure('sp_getLikeStatus',(_wishId,_user),True)
            return json.dumps({'status':'OK','total':result[0][0],'likeStatus':result[0][1]})
        else:
            return render_template('error.html',error = 'An error occurred!')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
    
@app.route('/getAllWishes')
def getAllWishes():
    if session.get('user'):
        _user = session.get('user')
        result = callProcedure('sp_GetAllWishes',(_user,),True)
        wishes_dict = []
        for wish in result:
            wish_dict = {
                'Id': wish[0],
                'Title': wish[1],
                'Description': wish[2],
                'FilePath': wish[3],
                'Like':wish[4],
                'HasLiked':wish[5]}
            wishes_dict.append(wish_dict)
        return json.dumps(wishes_dict)
    else:
        return render_template('error.html', error = 'Unauthorized Access')
    
@app.route('/showDashboard')
def showDashboard():
    return render_template('dashboard.html')
    
@app.route('/showAddWish')
def showAddWish():
    return render_template('addWish.html')
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
    	file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
    	f_name = str(uuid.uuid4()) + extension
    	file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        return json.dumps({'filename':f_name})
    
@app.route('/addWish',methods=['POST'])
def addWish():
    if session.get('user'):
        _title = request.form['inputTitle']
        _description = request.form['inputDescription']
        _user = session.get('user')
        if request.form.get('filePath') is None:
            _filePath = ''
        else:
            _filePath = request.form.get('filePath')
             
        if request.form.get('private') is None:
            _private = 0
        else:
            _private = 1
             
        if request.form.get('done') is None:
            _done = 0
        else:
            _done = 1
            
        data = callProcedure('sp_addWish',(_title,_description,_user,_filePath,_private,_done),False)
        if len(data) is 0:
            return redirect('/userHome')
        else:
            return render_template('error.html',error = 'An error occurred!')
 
    else:
        return render_template('error.html',error = 'Unauthorized Access')
        
#getWish but its using a POST HTTP method???
@app.route('/getWish',methods=['POST'])
def getWish():
    try:
        if session.get('user'):
            _user = session.get('user')
            _limit = pageLimit
            _offset = request.form['offset']
            print _offset
            _total_records = 0
            #there is a js/html5 issue that is preventing me from drying this out.
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_GetWishByUser',(_user,_limit,_offset,_total_records))
            wishes = cursor.fetchall()
            
            
            cursor.close()
            cursor = con.cursor()
            cursor.execute('SELECT @_sp_GetWishByUser_3');
            outParam = cursor.fetchall()

            response = []
            wishes_dict = []
            for wish in wishes:
                wish_dict = {
                        'Id': wish[0],
                        'Title': wish[1],
                        'Description': wish[2],
                        'Date': wish[4]}
                wishes_dict.append(wish_dict)
            response.append(wishes_dict)
            response.append({'total':outParam[0][0]}) 
            
            return json.dumps(response)
        else:
            return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))

#getWishById but its using a POST HTTP method???
@app.route('/getWishById',methods=['POST'])
def getWishById():
    if session.get('user'):
 
        _id = request.form['id']
        _user = session.get('user')
        result = callProcedure('sp_GetWishById',(_id,_user),True)
 
        wish = []
        wish.append({'Id':result[0][0],'Title':result[0][1],'Description':result[0][2],'FilePath':result[0][3],'Private':result[0][4],'Done':result[0][5]})
 
        return json.dumps(wish)
    else:
        return render_template('error.html', error = 'Unauthorized Access')
 
@app.route('/updateWish', methods=['POST'])
def updateWish():
    if session.get('user'):
        _user = session.get('user')
        _title = request.form['title']
        _description = request.form['description']
        _wish_id = request.form['id']
        _filePath = request.form['filePath']
        _isPrivate = request.form['isPrivate']
        _isDone = request.form['isDone']

        data = callProcedure('sp_updateWish',(_title,_description,_wish_id,_user,_filePath,_isPrivate,_isDone),False)
 
        if len(data) is 0:
            return json.dumps({'status':'OK'})
        else:
            return json.dumps({'status':'ERROR'})
        
@app.route('/deleteWish',methods=['POST'])
def deleteWish():
    if session.get('user'):
        _id = request.form['id']
        _user = session.get('user')
 
        result = callProcedure('sp_deleteWish',(_id,_user),False)
 
        if len(result) is 0:
            return json.dumps({'status':'OK'})
        else:
            return json.dumps({'status':'An Error occured'})
    else:
        return render_template('error.html',error = 'Unauthorized Access')
    
@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')
        
@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/showSignin')
def showSignin():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    _username = request.form['inputEmail']
    _password = request.form['inputPassword']
    
    data = callProcedure('sp_validateLogin',(_username,),True)
    
    if len(data) > 0:
        if check_password_hash(str(data[0][3]),_password):
            session['user'] = data[0][0]
            return redirect('/showDashboard')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    else:
        return render_template('error.html',error = 'Wrong Email address or Password.')\
        
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')
    
@app.route('/signUp',methods=['POST','GET'])
def signUp():
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    # validate the received values
    if _name and _email and _password:
        _hashed_password = generate_password_hash(_password)
        data = callProcedure('sp_createUser',(_name,_email,_hashed_password),False)
        if len(data) is 0:
            return json.dumps({'success':'1'})
        else:
            return json.dumps({'error':str(data[0]),'success':'0'})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})

if __name__ == "__main__":
    app.run(debug = True)