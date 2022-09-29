from ctypes import pointer
from flask import Flask, render_template, url_for, request, redirect
import ibm_db

app = Flask(__name__)
app.secret_key = "aezakmi"

conn = ibm_db.connect("DATABASE=<database>;HOSTNAME=<HOSTNAME_URL>;PORT=<PORT_NUM>;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=<USERNAME>;PWD=<PASSWORD>", "", "")

@app.route("/")
def home_page():
    users = []
    sql = "SELECT * FROM users"
    stmt = ibm_db.exec_immediate(conn, sql)
    dictionary = ibm_db.fetch_both(stmt)
    while dictionary != False:
        users.append(dictionary)
        dictionary = ibm_db.fetch_both(stmt)
    print(users)
    return render_template("index.html", users = users)

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/user/<id>")
def user_page(id):
    query = f"SELECT * FROM users WHERE email='{id}'"
    stmt = ibm_db.exec_immediate(conn, query)
    user = ibm_db.fetch_both(stmt)
    print(user)
    return render_template("userInfo.html", user=user)

@app.route("/accessbackend", methods=['POST', 'GET'])
def accessbackend():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        e_mail = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        dob = request.form['dob']

        query = "SELECT * FROM users WHERE email =?"
        stmt = ibm_db.prepare(conn, query)
        ibm_db.bind_param(stmt,1,e_mail)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return redirect(url_for("signin"))
        else:
            insert_sql = "INSERT INTO users VALUES (?,?,?,?,?,?)"
            prep_stmt = ibm_db.prepare(conn, insert_sql)
            ibm_db.bind_param(prep_stmt, 1, str(firstname))
            ibm_db.bind_param(prep_stmt, 2, str(lastname))
            ibm_db.bind_param(prep_stmt, 3, str(e_mail))
            ibm_db.bind_param(prep_stmt, 4, str(phone))
            ibm_db.bind_param(prep_stmt, 5, str(password))
            ibm_db.bind_param(prep_stmt, 6, str(dob))
            ibm_db.execute(prep_stmt)

        return redirect(url_for("home_page"))

    else:
        temp_user_eamil = request.args.get('email')
        temp_user_password = request.args.get('password')

        print(temp_user_eamil, temp_user_password)
        query = f"SELECT password FROM users WHERE email='{temp_user_eamil}'"
        stmt = ibm_db.exec_immediate(conn, query)
        dictionary = ibm_db.fetch_both(stmt)
        print(dictionary)
        if dictionary:
            if temp_user_password == dictionary['PASSWORD']:
                return redirect(url_for("user_page", id=temp_user_eamil))
            print(dictionary['PASSWORD']) # Shows actuall password if incorrect in terminal
        return redirect(url_for("signin"))