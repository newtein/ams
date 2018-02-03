from flask import Flask, render_template, request,session,url_for,redirect,flash
import psycopg2 as p
import all_func as af


app = Flask(__name__)
con=p.connect("dbname='NZ' user='harshit'")


@app.route('/',methods=["GET","POST"])
def index():
    emp_details = af.getempdetails(con)
    if request.method=="POST":

        if "Like" in request.form:
            set_login()
        elif "yes" in request.form and session['f_data']:
                td1 = request.form['td1']
                td2 = request.form['td2']
                af.delUp_attendence(session["id"], td1, td2, session['f_data'], con)
                p = "Your changes are successfully recorded!!"
                data_t=(session["name"],session["type"],p,emp_details)
                return render_template('dashboard.html', data_t=data_t)

        elif "admin_att_edit" in request.form and (session["type"] =="HR" or session["type"]=="admin"):
            print("-->",request.form)
            comment=request.form['comment']
            emp_name=request.form['emp_name']
            eid=emp_name.split("/")[0]
            if comment=="Correct Attendence":
                walkin=request.form['walkin']
                walkout = request.form['walkout']
                edit_date=request.form['edit_date']
                if walkin!="" and walkout!="" and edit_date!="":
                    reply=af.edit_attendence(eid,walkin,walkout,edit_date,con)
                    data_t = (session["name"], session["type"], reply, emp_details)
                    return render_template('dashboard.html', data_t=data_t)
                else:
                    data_t = (session["name"], session["type"],"**All fields are required.", emp_details)
                    return render_template('dashboard.html', data_t=data_t)


            else:
                to=request.form['to']
                frm = request.form['frm']
                if to!="" and frm!="":
                    af.delUp_attendence(session["id"], frm, to, comment, con)
                    p = "Your changes are successfully recorded!!"
                    data_t = (session["name"], session["type"], p, emp_details)
                    return render_template('dashboard.html', data_t=data_t)
                else:
                    data_t = (session["name"], session["type"], "**All fields are required.", emp_details)
                    return render_template('dashboard.html', data_t=data_t)
            data_t = (session["name"], session["type"], None, emp_details)
            return render_template('dashboard.html', data_t=data_t)


        else:
            to=request.form["to"]
            frm=request.form["from"]
            notig,td1,td2=af.check_date(session["id"],frm,to,con)
            if notig=="safe":
                print("safe")
                p="Your changes are successfully recorded!!"
                af.update_attendence(session["id"],td1,td2,request.form,con)
                data_t = (session["name"], session["type"], p, emp_details)
                return render_template('dashboard.html', data_t=data_t)
            else:
                print("not safe")

                session['f_data']=request.form
                print(td1,td2)
                data_t = (session["name"], session["type"], "confirm", emp_details)
                return render_template('dashboard.html', data_t=data_t,td1=td1,td2=td2)



    if "username" in session:
        data_t = (session["name"], session["type"], None, emp_details)
        t_date,t_time="",""

        if session["in"]==0:
            t_date, t_time=af.save_att(session["id"],"walkin",con)
            session["in"]=1
        if session["type"] == "EMP":
            return render_template('dashboard.html', data_t=data_t,date=t_date,time=t_time)
        elif session["type"] == "HR":
            return render_template('dashboard.html', data_t=data_t,date=t_date,time=t_time)

    return render_template('hello.html')



@app.route("/logout")
def logout():
    t_date,t_time=af.save_att(session["id"],"walkout",con)
    session.clear()

    flash('Your attendence is successfully locked at '+t_date+' '+t_time+'.\n BBye and See you!!')
    return redirect(url_for("index"))


@app.route('/newemployee',methods=["POST","GET"])
def newemployee():
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
        cur=con.cursor()
        try:
                cur.execute("insert into emp_details values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(empid,name,email,phone,ephone,dob,privel,desig,bgroup,joining,cur_address,cur_city,cur_state))
                con.commit()
                p="Form successfully submitted"
                fmt="success"
                e="success"
                cur.close()
                data_t = (session["name"], session["type"], p, af.get_emp_list(con))
                return render_template('newemployee.html', data_t=data_t, fmt=fmt)
        except Exception, e:
            p = e
            fmt = "danger"
            data_t = (session["name"], session["type"], e, af.get_emp_list(con))
            return render_template('newemployee.html', data_t=data_t, fmt=fmt)



    else:
         data_t = (session["name"], session["type"], None, af.get_emp_list(con))
         return render_template('newemployee.html',data_t=data_t)


@app.route('/admin_att',methods=["POST","GET"])
def admin_att():
    data_t = (session["name"], session["type"],None,af.get_emp_list(con))
    if request.method=="POST":
        to = request.form['adminto']
        frm = request.form['adminfrom']
        if to!="" and frm!="":
            att_detail,path=af.get_col_att(to,frm,con)
            return render_template('admin_att.html', data_t=data_t, id=session["id"], to=to,
                                   frm=frm,d=att_detail,path=path)
        else:
            return render_template('admin_att.html', data_t=data_t, id=session["id"], to="", frm="")


    else:
        return render_template('admin_att.html',data_t=data_t,id=session["id"],to="",frm="")


@app.route('/view',methods=["POST","GET"])
def view():
    data_t = (session["name"], session["type"],None,af.get_emp_list(con))
    if request.method=="POST":
        to = request.form['to']
        frm = request.form['from']
        if to!="" and frm!="":
            if "ssid" in request.form:
                att_detail = af.getdateobj(to, frm, request.form["ssid"], con)
                return render_template('view.html', data_t=data_t, id=session["id"], to=to,
                                       frm=frm, d=att_detail)

            elif "empatt" in request.form:
                att_detail=af.getdateobj(to,frm,session["id"],con)
                return render_template('view.html',data_t=data_t , id=session["id"], to=to,
                                       frm=frm,d=att_detail)
    else:
        return render_template('view.html',data_t=data_t,id=session["id"],to="",frm="")



@app.route('/request_at')
def request_at():
    data_t = (session["name"], session["type"],None,af.get_emp_list(con))
    return render_template('request_at.html', data_t=data_t, id=session["id"])

@app.route('/emp_view')
def emp_view():
    data_t = (session["name"], session["type"],None,af.get_emp_list(con))
    emp_details=af.getempdetails(con)
    return render_template('emp_view.html',data_t=data_t,e=emp_details)


def set_login():
    attem_user = request.form['username']
    attem_pass = request.form['password']
    cur = con.cursor()
    cur.execute("select id,name,password,type from emp_login where username='" + attem_user + "';")
    data = cur.fetchone()
    cur.close()
    id = data[0]
    name = data[1]
    type = data[3]
    if data:
        password = data[2]
        if (password == attem_pass):
            session["id"] = id
            session["username"] = attem_user
            session["type"] = type
            session["name"] = name
            session["in"] = 0



if __name__ == "__main__":
    app.secret_key="nyalazone"
    app.run(debug=True)