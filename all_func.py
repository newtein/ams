from datetime import timedelta,date,datetime
from collections import OrderedDict
import ntplib,datetime
import xml.etree.ElementTree as et


def get_password(id,con):
    cur=con.cursor()
    cur.execute("select password from emp_login where id=%s",[id])
    result=cur.fetchone()
    cur.close()
    if len(result)>0:
        return result
    else:
        return None


def set_newpassword(id,newpass1,con):
    try:
        cur = con.cursor()
        cur.execute("update emp_login set password=%s where id=%s", [newpass1,id])
        con.commit()
        cur.close()
        return "success"
    except Exception, e:
        return e


def mac_parser(filename,remark, con):
    tree = et.parse(filename)
    print("++"+filename)
    root = tree.findall("host")
    for host in root:
        for mac in host.findall("address"):
            if (mac.get('addrtype') == 'mac'):
                #print(mac.get("addr"))
                macaddr=mac.get("addr")
                #print(macaddr)
                cur=con.cursor()
                cur.execute('''select id from emp_login where macaddr=%s and active=1''',[macaddr.lower()])
                result=cur.fetchone()
                #print(result)
                if(result!=None):
                   print(result[0],remark)
                   save_att(result[0],remark,con)
                cur.close()


def del_attendence(id,new_d,con):
    cur = con.cursor()
    cur.execute("delete from attendence where id=%s and d_date=%s;", (id, new_d))
    con.commit()
    cur.close()


def validate_date(d):
    try:
        datetime.datetime.strptime(d, '%Y-%m-%d')
        return 1
    except:
        return 0

def validate_slash_date(d):
    try:
        datetime.datetime.strptime(d, '%m/%d/%Y')
        return 1
    except:
        return 0

def validate_time(t):
    try:
        datetime.datetime.strptime(t, '%H:%M')
        return 1
    except:
        return 0

def update_emp(id,comment,con):
    if comment=="Enable":
        ask=1
    else:
        ask=0
    cur = con.cursor()
    cur.execute("update emp_login set active=%s where id=%s;", (ask, id))
    con.commit()
    cur.close()
    return "Employee is Modified"


def edit_attendence(id,walkin,walkout,edit_date,con):
    result=check_for_entry(id,edit_date,con)
    if result==1:
        del_attendence(id,edit_date,con)
    try:
        cur = con.cursor()
        cur.execute("insert into attendence (id,d_date,t_time,remark) values (%s,%s,%s,'walkin')",(id,edit_date,walkin))
        cur.execute("insert into attendence (id,d_date,t_time,remark) values (%s,%s,%s,'walkout')",(id,edit_date,walkout))
        con.commit()
        cur.close()
        return "Records successfully modified!"
    except Exception, e:
        return e


def check_for_entry(id,edit_date,con):
    cur = con.cursor()
    cur.execute('''select * from attendence where id=%s and d_date=%s''', [id, edit_date])
    if (len(cur.fetchall()) > 0):
        return 1
    return 0

def get_emp_list(con):
    cur=con.cursor()
    cur.execute("select id,name from emp_details order by id")
    el=cur.fetchall()
    cur.close()
    return el


def download_file(d,frm,to):
    path="static/files/attendence.csv"
    f=open(path,"w+")
    f.write("Date,  ,")
    for l in d.values()[0]:
           f.write(l[1]+", ")
    f.write("\n")
    for date in d:
      f.write(date+", WalkIn, ")
      for ids in d[date]:
        if d[date][ids][0][0] == "Not Marked":
            f.write(str(d[date][ids][0][0])+", ")
        elif d[date][ids][0][0] != "Regular":
            f.write(str(d[date][ids][0][0])+", ")
        else:
            f.write(str(d[date][ids][0][1])+", ")
      f.write("\n")
      f.write(date + ", WalkOut, ")
      for ids in d[date]:
        if d[date][ids][0][0] == "Not Marked":
              f.write(str(d[date][ids][0][0])+", ")
        elif d[date][ids][0][0] != "Regular":
              f.write(str(d[date][ids][0][0])+", ")
        else:
              f.write(str(d[date][ids][0][2])+", ")
      f.write("\n")
    f.close()
    return path


def save_att(id,remark,con):
    # try:
    #
    #     x = ntplib.NTPClient()
    #     f=datetime.datetime.utcfromtimestamp(x.request('europe.pool.ntp.org').tx_time)
    #     diff=timedelta(hours=5.5)
    #     f=f+diff
    # except:
    f = datetime.datetime.now()


    d_date = str(f.year) + '-' + str(f.month) + '-' + str(f.day)
    t_time = str(f.hour) + ':' + str(f.minute) + ':' + str(f.second)
    inout=check_in_out(id,d_date,con)
    print(inout)
    if(inout==1):
        del_prev_remark(id,d_date,con)
    if remark=="walkin":
        notig=check_if(id,d_date,remark,con)
        if notig == 0:
                print("Not again")
                cur = con.cursor()
                cur.execute('''insert into attendence values (%s, %s, %s, %s)''',[id,d_date,t_time,remark])
                con.commit()
                cur.close()
                return d_date, t_time
    elif remark=="walkout":
        notig = check_if(id, d_date, remark, con)
        if(notig==1):
            print("deleting")
            del_early_walkout(id, d_date, remark, con)
        cur = con.cursor()
        cur.execute('''insert into attendence values (%s, %s, %s, %s)''', [id, d_date, t_time, remark])
        con.commit()
        cur.close()
        return d_date, t_time
    return "", ""


def del_early_walkout(id,d_date,remark,con):
    cur = con.cursor()
    cur.execute('''delete from attendence where id=%s and d_date=%s and remark=%s''', [id, d_date, remark])
    con.commit()
    cur.close()


def del_prev_remark(id, d, con):
    cur = con.cursor()
    cur.execute("delete from attendence where id=%s and d_date=%s and remark!='walkin' and remark!='walkout'", [id, d])
    con.commit()
    cur.close()


def check_if(id,d,remark,con):
    cur = con.cursor()
    cur.execute('''select * from attendence where id=%s and d_date=%s and remark=%s''', [id, d,remark])
    if(len(cur.fetchall())>0):
        return 1
    return 0


def check_in_out(id,d,con):
    cur=con.cursor()
    cur.execute("select * from attendence where id=%s and d_date=%s and remark!='walkin' and remark!='walkout';",(id,d))
    if len(cur.fetchall()) > 0:
        return 1
    return 0


def get_col_att(to,frm,con):
    cur2=con.cursor()
    cur2.execute("select distinct id, name from emp_login where active=1 order by id;")
    id_list=cur2.fetchall()
    d1, d2 = process_date(frm, to, "-")
    delta=d2-d1
    att_data = OrderedDict()
    cur = con.cursor()
    for i in range(delta.days + 1):
        new_d = d1 + timedelta(days=i)
        att_data[str(new_d)] = OrderedDict()
        for l in id_list:
            if (l[0],l[1]) not in att_data:
                att_data[str(new_d)][(l[0],l[1])]=[]
            cur.execute("select remark,t_time from attendence where d_date=%s and id=%s;", (new_d, l[0]))


            if new_d.weekday() == 5 or new_d.weekday() == 6:
                att_data[str(new_d)][(l[0],l[1])].append(["WEEKEND", None, None])
            else:
                lp = cur.fetchall()
                if len(lp) == 2:
                    if lp[0][0]=="walkout":
                        print("here333")
                        lp[0],lp[1]=lp[1],lp[0]
                    print(lp)
                    att_data[str(new_d)][(l[0],l[1])].append(["Regular", str(lp[0][1]), str(lp[1][1])])
                elif len(lp) == 1 and (lp[0][0] == "walkin" or lp[0][0] == "walkout"):
                    print(lp, len(lp))
                    if lp[0][0] == "walkin":
                        att_data[str(new_d)][(l[0],l[1])].append( ["Regular", str(lp[0][1]), None])
                    else:
                        att_data[str(new_d)][(l[0],l[1])].append( ["Regular", None, str(lp[0][1])])
                elif len(lp) == 0:
                    att_data[str(new_d)][(l[0],l[1])].append(["Not Marked", None, None])
                else:
                    print("here2 ", new_d, lp)
                    att_data[str(new_d)][(l[0],l[1])].append( [lp[0][0], None, None])

    cur.close()
    cur2.close()
    path=download_file(att_data,frm,to)

    return att_data,path


def getdateobj(to,frm,id,con):
    d1,d2=process_date(frm,to,"-")
    print(d1,d2)
    delta=d2-d1
    att_data=OrderedDict()
    cur = con.cursor()
    for i in range(delta.days+1):
        new_d=d1+timedelta(days=i)
        cur.execute("select remark,t_time from attendence where d_date=%s and id=%s;",(new_d,id))
        if new_d.weekday()==5 or new_d.weekday()==6:
            att_data[str(new_d)] =["WEEKEND",None,None]
        else:
            lp=cur.fetchall()
            if len(lp)==2:
                print("here1 ",new_d)
                att_data[str(new_d)]=["Regular",lp[0][1],lp[1][1]]
            elif len(lp)==1 and (lp[0][0]=="walkin" or  lp[0][0]=="walkout"):
                print(lp,len(lp))
                if lp[0][0]=="walkin":
                    att_data[str(new_d)] = ["Regular", lp[0][1], None]
                else:
                    att_data[str(new_d)] = ["Regular", None, lp[0][1]]
            elif len(lp)==0:
                att_data[str(new_d)] = ["Not Marked", None, None]
            else:
                print("here2 ", new_d,lp)
                att_data[str(new_d)] = [lp[0][0],None ,None]
    cur.close()

    return att_data


def getempdetails(dp,con):
    cur = con.cursor()
    if dp=="*":
         cur.execute("select id,name,email,phone,ephone,dob,designation,bgroup,doj,cur_add,cur_city,cur_state,status from emp_details order by id ;")
    else:
         cur.execute(
            "select id,name,email,phone,ephone,dob,designation,bgroup,doj,cur_add,cur_city,cur_state,status from emp_details where id=%s ;",[dp])

    emp_details=cur.fetchall()
    return emp_details


def add_mac(eid,mac,con):
    cur=con.cursor()
    cur.execute("update emp_login set macaddr=%s where id=%s",[mac,eid])
    con.commit()
    cur.close()
    return "MAC Modified Successfully"

def set_status(id, status, con):
    cur = con.cursor()
    cur.execute("update emp_details set status=%s where id=%s", [status, str(id)])
    con.commit()
    cur.close()
    return "Status modified Successfully"

def process_date(frm,to,deli):
    l1 = frm.split(deli)
    l2 = to.split(deli)
    l1 = [int(tl) for tl in l1]
    l2 = [int(tl) for tl in l2]
    if deli=="/":
            d1 = date(l1[2], l1[0], l1[1])
            d2 = date(l2[2], l2[0], l2[1])
    else:
        d1 = date(l1[0], l1[1], l1[2])
        d2 = date(l2[0], l2[1], l2[2])
    return d1,d2


def check_date(id,frm,to,con):
    print(frm,to)
    d1,d2=process_date(frm,to,"/")
    delta = d2 - d1
    att_data = OrderedDict()
    cur = con.cursor()

    for i in range(delta.days + 1):
        new_d = d1 + timedelta(days=i)
        cur.execute("select * from attendence where d_date=%s and id=%s;", (new_d, id))
        if len(cur.fetchall())>0:
            print new_d,d1,d2
            return new_d,d1,d2

    cur.close()
    return "safe",d1,d2


def update_attendence(id,frm,to,l,con):

    for i in l:
        if i!="to" and i!="from":
            reason=i
    delta = to-frm
    for i in range(delta.days + 1):
        new_d = frm + timedelta(days=i)
        cur = con.cursor()
        cur.execute("insert into attendence(id,d_date,remark) values (%s,%s,%s);",(id,new_d,reason))
        con.commit()
        cur.close()


def delUp_attendence(id,frm,to,l,con):
    if type(l)==dict:
        for i in l:
            if i!="to" and i!="from":
                reason=i
    else:
        reason=l
    frm, to=process_date(frm,to,"-")
    delta = to-frm
    for i in range(delta.days + 1):
        new_d = frm + timedelta(days=i)
        cur = con.cursor()
        cur.execute("delete from attendence where id=%s and d_date=%s;",(id,new_d))
        con.commit()
        cur2 = con.cursor()
        cur2.execute("insert into attendence(id,d_date,remark) values (%s,%s,%s);", (id, new_d, reason))
        con.commit()
        cur.close()
        cur2.close()