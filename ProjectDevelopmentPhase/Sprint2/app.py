import json
from flask import Flask, render_template, request, redirect, url_for, session
import ibm_db
import uuid
import sendemail

app = Flask(__name__)
app.secret_key = "password"

conn = ibm_db.connect("DATABASE=<database>;HOSTNAME=<hostname>;PORT=<port>;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=<user>;PWD=<password>", "", "")

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def signin():
    try:
        msg = request.args['msg']
    except:
        msg = ""
    return render_template('signin.html', msg=msg)

@app.route("/signup")
def signup():
    return render_template('signup.html')

@app.route("/forgot")
def forgot():
    return render_template('forgotpass.html')

@app.route("/profile")
def profile():
    user = request.args['user']
    user=json.loads(user)

    # fetch user professional profile
    query = f"SELECT * FROM skillset WHERE c_id='{user['C_ID']}'"
    stmt = ibm_db.exec_immediate(conn, query)
    data = ibm_db.fetch_both(stmt)

    # fetch all eligible jobs
    openings = []
    skillssss = data['SKILLS'].split(',')
    print(skillssss)
    for i in skillssss:
        if i == '':
            continue
        query = f"SELECT * FROM openings WHERE REGEXP_LIKE (req_skill, '\\b{i.strip()}\\b', 'i')"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            if dictionary not in openings:
                openings.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)

    return render_template('userprofile.html', user=user, data=data, openings=openings)

@app.route("/recruitment")
def recruitment():
    user = request.args['user']
    user=json.loads(user)

    # fetch all posted job opennings
    data = []
    query = f"SELECT * FROM openings WHERE c_id='{user['C_ID']}'"
    stmt = ibm_db.exec_immediate(conn, query)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        data.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)

    # fetch all eligible candidates
    candid = []
    for job in data:
        if job == '':
            continue
        skillls = job['REQ_SKILL'].split(',')
        
        for i in skillls:
            query = f"SELECT * FROM skillset WHERE REGEXP_LIKE (SKILLS, '\\b{i.strip()}\\b', 'i')"
            stmt = ibm_db.exec_immediate(conn, query)
            dictionary = ibm_db.fetch_both(stmt)
            
            while dictionary != False:
                if dictionary not in candid:
                    candid.append(dictionary)
                dictionary = ibm_db.fetch_both(stmt)

    candid_info = []
    for i in candid:
        query = f"SELECT c_id, firstname, lastname FROM customer where c_id='{i['C_ID']}'"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        
        while dictionary != False:
            if dictionary not in candid:
                candid_info.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
    print(candid_info)
    return render_template('recruitmentpage.html', user=user, data=data, candidates=candid, info=candid_info)

@app.route("/postjob")
def postjob():
    user = request.args.get('user')
    user = user.replace("\'", '\"')
    user = json.loads(user)
    return render_template('postjob.html', user=user)

@app.route("/updateprofile")
def updateprofile():
    user = request.args.get('user')
    user = user.replace("\'", '\"')
    user = json.loads(user)
    return render_template('userupdate.html', user=user)

@app.route("/modifyskills", methods=['POST', 'GET'])
def modifyskills():
    if request.method == 'POST':
        c_id = request.form['c_id']
        skills = request.form.getlist('skill')
        project = request.form.getlist('project')
        project_des = request.form.getlist('project_des')
        address = request.form['address'].replace('\'', " ").replace('\"', " ")
        linkedin = request.form['linkedin'].replace('\'', " ").replace('\"', " ")
        github = request.form['github'].replace('\'', " ").replace('\"', " ")
        achieve = request.form.getlist('achievement')
        des = request.form['des'].replace('\'', " ").replace('\"', " ")
        query = f"UPDATE skillset SET skills='{','.join(skills)}', project='{','.join(project)}', project_des='{','.join(project_des)}', address='{address}', linkedin='{linkedin}', github='{github}', achieve='{','.join(achieve)}', des='{des}' WHERE c_id='{c_id}'"
        print(query)
        update_stmt = ibm_db.prepare(conn, query)
        ibm_db.execute(update_stmt)
        query = f"SELECT * FROM customer WHERE c_id='{c_id}'"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        dictionary = json.dumps(dictionary)
    return redirect(url_for('profile', user=dictionary))

@app.route("/addjobs", methods=['POST', 'GET'])
def addjob():
    if request.method == 'POST':
        c_id = request.form['c_id']
        organization = request.form['organization'].replace('\'', " ").replace('\"', " ")
        title = request.form['title'].replace('\'', " ").replace('\"', " ")
        des = request.form['des'].replace('\'', " ").replace('\"', " ")
        req_skill = request.form.getlist('req_skill')
        location = request.form.getlist('location')
        query = f"INSERT INTO openings VALUES ('{c_id}', '{organization}', '{title}', '{des}', '{','.join(req_skill)}', '{','.join(location)}')"
        update_stmt = ibm_db.prepare(conn, query)
        ibm_db.execute(update_stmt)
        query = f"SELECT * FROM customer WHERE c_id='{c_id}'"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        dictionary = json.dumps(dictionary)
    return redirect(url_for('recruitment', user=dictionary))

@app.route("/accessbackend", methods=['POST', 'GET'])
def accessbackend():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        account_type = request.form['accounttype']

        query = "SELECT * FROM customer WHERE email =?"
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return "user exists"
        else:
            insert_query = "INSERT INTO customer VALUES (?,?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_query)
            c_id = str(uuid.uuid4().hex)
            ibm_db.bind_param(prep_stmt, 1, c_id)
            ibm_db.bind_param(prep_stmt, 2, str(firstname))
            ibm_db.bind_param(prep_stmt, 3, str(lastname))
            ibm_db.bind_param(prep_stmt, 4, str(email))
            ibm_db.bind_param(prep_stmt, 5, str(phone))
            ibm_db.bind_param(prep_stmt, 6, str(password))
            ibm_db.bind_param(prep_stmt, 7, str(account_type))
            ibm_db.execute(prep_stmt)
            if account_type == 'user':
                query = f"INSERT INTO skillset VALUES ('{c_id}', '','','','','','','','')"
                stmt = ibm_db.prepare(conn, query)
                ibm_db.execute(stmt)
        
        return redirect(url_for('signin', msg="Account Created"))
    
    else:
        temp_user_email = request.args.get('email')
        temp_user_password = request.args.get('password')
        msg = ''

        query = f"SELECT * FROM customer WHERE email='{temp_user_email}'"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        
        if dictionary:
            if temp_user_password == dictionary['PASSWORD']:
                if dictionary['ACCOUNT_TYPE'] == 'user':
                    dictionary = json.dumps(dictionary)
                    return redirect(url_for('profile', user=dictionary))
                else:
                    dictionary = json.dumps(dictionary)
                    return redirect(url_for('recruitment', user=dictionary))
            else:
                print(dictionary['PASSWORD'])
                msg = "wrong password"
                return redirect(url_for('signin', msg=msg))
        msg = "No user found"
        return redirect(url_for('signin', msg=msg))

@app.route("/sendmail/<mail>")
def sendmail(mail):
    query = f"SELECT password FROM customer WHERE email='{mail}'"
    stmt = ibm_db.exec_immediate(conn, query)
    dictionary = ibm_db.fetch_both(stmt)
    if dictionary:
        sendemail.send_mail(mail, dictionary['PASSWORD'])
    return 'sent'

@app.route("/search")
def search():
    offers = []
    query = f"SELECT * FROM openings"
    stmt = ibm_db.exec_immediate(conn, query)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        if dictionary not in offers:
            offers.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    return render_template('searchpage.html', offers=offers)

@app.route("/searchbackend", methods=['GET'])
def searchbackend():
    offers = []
    if request.method == 'GET':
        print(request.form)
        search = request.args.get('searchval')
        query = f"SELECT * FROM openings WHERE REGEXP_LIKE (req_skill, '\\b{search.strip()}\\b', 'i')"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            if dictionary not in offers:
                offers.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
        query = f"SELECT * FROM openings WHERE REGEXP_LIKE (title, '\\b{search.strip()}\\b', 'i')"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        while dictionary != False:
            if dictionary not in offers:
                offers.append(dictionary)
            dictionary = ibm_db.fetch_both(stmt)
    return render_template('searchpage.html', offers=offers)

if __name__ == '__main__':
    app.run(debug=True, port=5000, host="0.0.0.0")
