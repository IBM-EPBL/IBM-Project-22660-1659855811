from flask import Flask, render_template, url_for, request, redirect
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = "aezakmi"

@app.route("/")
def home_page():
    con = sql.connect("user_base.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from users")

    users = cur.fetchall()
    con.close()
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
    with sql.connect("user_base.db") as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute(f"SELECT * FROM users WHERE email='{id}'")
        user = cur.fetchall()
    return render_template("userInfo.html", user=user[0])

@app.route("/accessbackend", methods=['POST', 'GET'])
def accessbackend():
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            e_mail = request.form['email']
            phone = request.form['phone']
            password = request.form['password']
            dob = request.form['dob']

            with sql.connect("user_base.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (firstname, lastname, email, phone, password, dob) VALUES (?,?,?,?,?,?)", (str(firstname), str(lastname), str(e_mail), str(phone), str(password), str(dob)))
                con.commit()
                msg = "You are Registerd!!"
        except:
            con.rollback()
            msg = "Some tech glitch!!"

        finally:
            print(msg)
            return redirect(url_for("home_page"))
    else:
        try:
            temp_user_eamil = request.args.get('email')
            temp_user_password = request.args.get('password')

            print(temp_user_eamil, temp_user_password)
            with sql.connect("user_base.db") as con:
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute(f"SELECT password FROM users WHERE email='{temp_user_eamil}'")
                user = cur.fetchall()
        except:
            print("error")
            con.rollback()
        finally:
            if len(user) > 0:
                if temp_user_password == user[0][0]:
                    return redirect(url_for("user_page", id=temp_user_eamil))
                print(user[0][0]) # Shows actuall password if incorrect in terminal
            return redirect(url_for("signin"))