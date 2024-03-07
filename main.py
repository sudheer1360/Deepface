from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from deepface import DeepFace

cluster=MongoClient('mongodb://localhost:27017')
db=cluster['face']
users=db['users']

app = Flask(__name__)
app.secret_key = '123'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login',methods=['post','get'])
def login():
    user=request.form['username']
    password=request.form['password']
    res=users.find_one({"username":user})
    if res and dict(res)['password']==password:
        return render_template('index.html')
    else:
        return render_template('login.html',status='User does not exist or wrong password')


@app.route('/reg')
def reg():
    return render_template('signup.html')

@app.route('/regis',methods=['post','get'])
def register():
    username=request.form['username']
    password=request.form['password']

    k={}
    k['username']=username
    k['password']=password 
    res=users.find_one({"username":username})
    if res:
        return render_template('login.html',status="Username already exists")
    else:
        users.insert_one(k)
        return render_template('signup.html',status="Registration successful")


@app.route('/index', methods=['GET', 'POST'])
def indexpage():
    result = None
    stat = None

    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file1' not in request.files or 'file2' not in request.files:
            return render_template('index.html', error="Please select two files to upload.")

        file1 = request.files['file1']
        file2 = request.files['file2']

        # If user does not select file, browser also
        # submit an empty part without filename
        if file1.filename == '' or file2.filename == '':
            return render_template('index.html', error="Please select two files to upload.")

        try:
            file1_path = "uploads/" + file1.filename
            file2_path = "uploads/" + file2.filename
            file1.save(file1_path)
            file2.save(file2_path)

            # Perform face verification
            result = DeepFace.verify(img1_path=file1_path, img2_path=file2_path)
            print(result)
            stat=result['verified']
            print(stat)
            if stat is not None:
                if stat :
                    return render_template('index.html', status="Real")
                else:
                    return render_template('index.html',err="Fake")

        except Exception as e:
            return render_template('index.html', error=f"An error occurred: {str(e)}")
    
    
    
    # return render_template('index.html')
    

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5001,debug=True)