from flask import Flask, render_template, request,session,url_for,redirect,flash
import psycopg2 as p
from flask_mail import Message, Mail
import all_func as af
import hashlib

#messages
login_msg='Please login to enter. Dont mess around.  -_-'
logout_msg='BBye, See you again!!'
leave_msg="Don't Play Leave, Leave right now! :-D"
null_msg="Fill empty fields or check format Date: YYYY-MM-DD and Time: HH:MM!"
edit_success="Your changes are successfully recorded!!"
first_login="Cheers!! Your attendence is successfully locked at "
disabled_msg="Your profile is disabled please contact HR."
#end-messages

app = Flask(__name__)
mail=Mail(app)
con=p.connect("dbname='NZ' user='harshit'")


def ifsessionisset():
    if "username" and "password" and "name" in session:
        return 1
    else:
        return 0


@app.route('/',methods=["GET","POST"])
def index():
    emp_details = af.getempdetails("*",con)

    if request.method=="POST":
        if "Like" in request.form:
            set_login()
        elif "yes" in request.form and session['f_data']:
                td1 = request.form['td1']
                td2 = request.form['td2']
                af.delUp_attendence(session["id"], td1, td2, session['f_data'], con)
                p = edit_success
                data_t=(session["name"],session["type"],p,emp_details)
                return render_template('dashboard.html', data_t=data_t)

        elif "search_emp" in request.form:
            print(request.form["search"])
            emp_details = af.getempdetails(request.form["search"].split("/")[0],con)
            data_t = (session["name"], session["type"], None, emp_details)
            return render_template('dashboard.html', data_t=data_t)

        elif "admin_att_edit" in request.form and (session["type"] =="HR" or session["type"]=="admin"):
            comment=request.form['comment']
            emp_name=request.form['emp_name']
            if comment!='--Remark--' or emp_name!='--Select Employee--':
                eid=emp_name.split("/")[0]
                if comment=="Correct Attendence":
                    walkin=request.form['walkin']
                    walkout = request.form['walkout']
                    edit_date=request.form['edit_date']
                    if walkin!="" and walkout!="" and edit_date!="" and af.validate_date(edit_date) and af.validate_time(walkin) and af.validate_time(walkout):
                        reply=af.edit_attendence(eid,walkin,walkout,edit_date,con)
                        data_t = (session["name"], session["type"], reply, emp_details)
                        return render_template('dashboard.html', data_t=data_t)
                    else:
                        data_t = (session["name"], session["type"],null_msg, emp_details)
                        return render_template('dashboard.html', data_t=data_t)
                elif comment=="Enable" or comment=="Disable":
                    reply=af.update_emp(eid,comment,con)
                    data_t = (session["name"], session["type"], reply, emp_details)
                    return render_template('dashboard.html', data_t=data_t)
                elif comment=="Add Mac Address":
                    if request.form["mac"]!="":
                        mac=request.form["mac"]
                        reply=af.add_mac(eid,mac.lower(),con)
                        data_t = (session["name"], session["type"], reply, emp_details)
                        return render_template('dashboard.html', data_t=data_t)

                elif request.form['to']!="" and request.form['frm']!="":
                    print(request.form)
                    to=request.form['to']
                    frm = request.form['frm']
                    if to!="" and frm!="" and af.validate_date(to)and af.validate_date(frm) :
                        af.delUp_attendence(eid, frm, to, comment, con)
                        p = edit_success
                        data_t = (session["name"], session["type"], p, emp_details)
                        return render_template('dashboard.html', data_t=data_t)
                    else:
                        data_t = (session["name"], session["type"], null_msg, emp_details)
                        return render_template('dashboard.html', data_t=data_t)
                data_t = (session["name"], session["type"], None, emp_details)
                return render_template('dashboard.html', data_t=data_t)
            else:
                data_t = (session["name"], session["type"], None, emp_details)
                return render_template('dashboard.html', data_t=data_t)

        elif request.form['to']!="" and request.form['from']!="" and af.validate_slash_date(request.form['to']) and af.validate_slash_date(request.form['from']):
            to=request.form["to"]
            frm=request.form["from"]
            notig,td1,td2=af.check_date(session["id"],frm,to,con)
            if notig=="safe":
                print("safe")
                p=edit_success
                af.update_attendence(session["id"],td1,td2,request.form,con)
                data_t = (session["name"], session["type"], p, emp_details)
                return render_template('dashboard.html', data_t=data_t)
            else:
                print("not safe")
                session['f_data']=request.form
                #print(td1,td2)
                data_t = (session["name"], session["type"], "confirm", emp_details)
                return render_template('dashboard.html', data_t=data_t,td1=td1,td2=td2)
        else:
            print(request.form)
            data_t = (session["name"], session["type"],leave_msg, emp_details)
            return render_template('dashboard.html', data_t=data_t,p="")

    if "username" in session:
        data_t = (session["name"], session["type"], None, emp_details)
        t_date,t_time="",""
        if session["in"]==0:
            t_date, t_time=af.save_att(session["id"],"walkin",con)
            session["in"]=1
        if session["type"] == "EMP":
            return render_template('dashboard.html', data_t=data_t,date=t_date,time=t_time,login_success=first_login)
        elif session["type"] == "HR" or session["type"] == "admin" :
            return render_template('dashboard.html', data_t=data_t,date=t_date,time=t_time,login_success=first_login)

    return render_template('hello.html')


@app.route("/logout")
def logout():
    t_date,t_time=af.save_att(session["id"],"walkout",con)
    session.clear()
    flash('Your attendence is successfully locked at '+t_date+' '+t_time+" "+logout_msg)
    return redirect(url_for("index"))


@app.route("/add_status",methods=["POST","GET"])
def add_status():
    emp_details = af.getempdetails("*", con)
    if request.method=="POST":
        if request.form["status"]!="":
            reply=af.set_status(session["id"],request.form["status"],con)

            return redirect(url_for("index"))
        else:
            status = "Sometimes I left blanks in life and blank status"
            reply=af.set_status(session["id"], status, con)

            return redirect(url_for("index"))


    data_t = (session["name"], session["type"], None, af.get_emp_list(con))
    return render_template("add_status.html",data_t=data_t)


@app.route("/forgot_pass",methods=["POST","GET"])
def forgot_pass():
    if request.method=="POST":
        if request.form['remail']!="":
            msg = Message("Hello", sender="from@example.com", recipients=["harshitgujral12@gmail.com"])
            mail.send(msg)
            return render_template("forgot_pass.html")

    return render_template("forgot_pass.html")


@app.route('/newemployee',methods=["POST","GET"])
def newemployee():
    r = ifsessionisset()
    if r == 1:
        if request.method=="POST":
            empid=request.form['empid']
            cur_city = request.form['cur_city']
            name = request.form['full_name']
            desig = request.form['designation']
            bgroup = request.form['blood_group']
            dob = request.form['dob']
            cur_address = request.form['cur_address']
            phone = request.form['phone']
            privel = request.form['privel']
            cur_state = request.form['cur_state']
            ephone=request.form['ephone']
            email = request.form['email']
            joining = request.form['joining']

            try:
                cur = con.cursor()
                cur.execute("insert into emp_details values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(empid,name,email,phone,ephone,dob,privel,desig,bgroup,joining,cur_address,cur_city,cur_state))
                password=name.split()[0]
                con.commit()
                cur = con.cursor()
                cur.execute("insert into emp_login (id,username,name,password,type) values(%s,%s,%s,%s,%s) ",[empid,email,name,hashlib.sha1(password).hexdigest(),privel])
                con.commit()
                p="Form successfully submitted. Username: "+email+" Password: "+password+" All the best to "+name
                fmt="success"
                e="success"
                cur.close()
                print(p)
                data_t = (session["name"], session["type"], p, af.get_emp_list(con))
                return render_template('newemployee.html', data_t=data_t, fmt=fmt)
            except Exception, e:
                p = e
                fmt = "danger"
                data_t = (session["name"], session["type"], p, af.get_emp_list(con))
                return render_template('newemployee.html', data_t=data_t, fmt=fmt)
        else:
             data_t = (session["name"], session["type"], None, af.get_emp_list(con))
             return render_template('newemployee.html',data_t=data_t)
    else:
        flash(login_msg)
        return render_template('hello.html')


@app.route('/admin_att',methods=["POST","GET"])
def admin_att():
    r=ifsessionisset()
    if r == 1:
        data_t = (session["name"], session["type"],None,af.get_emp_list(con))
        if request.method=="POST":
            to = request.form['adminto']
            frm = request.form['adminfrom']
            if to!="" and frm!="" and af.validate_date(to) and af.validate_date(frm):
                att_detail,path=af.get_col_att(to,frm,con)
                return render_template('admin_att.html', data_t=data_t, id=session["id"], to=to,
                                       frm=frm,d=att_detail,path=path)
            else:
                return render_template('admin_att.html', data_t=data_t, id=session["id"], to="", frm="",msg=null_msg)


        else:
            return render_template('admin_att.html',data_t=data_t,id=session["id"],to="",frm="")
    else:
        flash(login_msg)
        return render_template('hello.html')


@app.route('/view',methods=["POST","GET"])
def view():
    r=ifsessionisset()
    if r==1:
        data_t = (session["name"], session["type"],None,af.get_emp_list(con))
        if request.method=="POST":
            if request.form['to']!="" and request.form['from']!="":
                to = request.form['to']
                frm = request.form['from']
                if to!="" and frm!="" and af.validate_date(to) and af.validate_date(frm):
                    if "ssid" in request.form:
                        att_detail = af.getdateobj(to, frm, request.form["ssid"], con)
                        return render_template('view.html', data_t=data_t, id=session["id"], to=to,
                                               frm=frm, d=att_detail)

                    elif "empatt" in request.form:
                        att_detail=af.getdateobj(to,frm,session["id"],con)
                        return render_template('view.html',data_t=data_t , id=session["id"], to=to,
                                               frm=frm,d=att_detail)
                else:
                    return render_template('view.html', data_t=data_t, id=session["id"], to="", frm="", msg="Format: YYYY-MM-DD")
            else:
                return render_template('view.html', data_t=data_t, id=session["id"], to="", frm="",msg=null_msg)
        else:
            return render_template('view.html',data_t=data_t,id=session["id"],to="",frm="")
    else:
        flash(login_msg)
        return render_template('hello.html')


@app.route('/request_at')
def request_at():
    r = ifsessionisset()
    if r==1:
        data_t = (session["name"], session["type"],None,af.get_emp_list(con))
        return render_template('request_at.html', data_t=data_t, id=session["id"])
    else:
        flash(login_msg)
        return render_template('hello.html')


@app.route('/emp_view')
def emp_view():
    r = ifsessionisset()
    if(r==1):
        data_t = (session["name"], session["type"],None,af.get_emp_list(con))
        emp_details=af.getempdetails(con)
        return render_template('emp_view.html',data_t=data_t,e=emp_details)
    else:
        flash(login_msg)
        return render_template('hello.html')


@app.route('/changepass',methods=["POST","GET"])
def changepass():
    if request.method=="POST":
        if request.form['oldpass']!="" and request.form['newpass1']!="" and request.form['newpass2']!="":
            oldpass=request.form['oldpass']
            newpass1=request.form['newpass1']
            newpass2 = request.form['newpass2']
            if newpass1==newpass2:
                oldpassword=af.get_password(session['id'],con)
                if hashlib.sha1(oldpass).hexdigest()==oldpassword[0] and oldpassword is not None:
                    result=af.set_newpassword(session['id'],hashlib.sha1(newpass1).hexdigest(),con)
                    if result=="success":
                        data_t = (session["name"], session["type"], "**Password successfully modified!",
                                  af.get_emp_list(con))
                        return render_template('changepass.html', data_t=data_t)
                    else:
                        data_t = (session["name"], session["type"], result,
                                  af.get_emp_list(con))
                        return render_template('changepass.html', data_t=data_t)

                else:
                    data_t = (session["name"], session["type"], "**Remember old password or try forgot password", af.get_emp_list(con))
                    return render_template('changepass.html', data_t=data_t)
            else:
                data_t = (session["name"], session["type"], "**New Password not match", af.get_emp_list(con))
                return render_template('changepass.html', data_t=data_t)

        else:
            data_t = (session["name"], session["type"], "**All fields are required", af.get_emp_list(con))
            return render_template('changepass.html', data_t=data_t)

    data_t = (session["name"], session["type"], None, af.get_emp_list(con))
    return render_template('changepass.html',data_t=data_t)


def set_login():
    if "username" and "password" in request.form:
        if request.form['username']!="" and request.form['password']!="":
            attem_user = request.form['username'].strip()
            attem_pass = request.form['password'].strip()
            cur = con.cursor()
            qr="select id,name,password,type,active from emp_login where username='" + attem_user + "';"
            cur.execute(qr)
            data = cur.fetchone()
            print(qr)
            cur.close()
            id = data[0]
            name = data[1]
            type = data[3]
            active = data[4]
            if data and active is 1:
                password = data[2]
                if (password == hashlib.sha1(attem_pass).hexdigest()):
                    session["id"] = id
                    session["username"] = attem_user
                    session["type"] = type
                    session["name"] = name
                    session["in"] = 0

            elif active is 0:
                flash(disabled_msg)
                return render_template('hello.html')


if __name__ == "__main__":
    app.secret_key="nyalazone"
    app.run(debug=True)