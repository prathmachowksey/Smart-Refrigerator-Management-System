import sqlite3

class AppVariables:
   productlist=[]
   con = sqlite3.connect('refrigerator.db')
   l1=[]
   with con:
                cur = con.cursor()
                cur.execute("SELECT productid,productname FROM products")
                rows = cur.fetchall()
                for row in rows:
                    pid = row[0]
                    pname = row[1]

                    #print(str(pid)+ " "+ pname)
                    t1=(str(pid),pname)
                    l1.append(t1)
                
   productlist=l1

   locationlist=[]
   con = sqlite3.connect('refrigerator.db')
   l2=[]
   with con:
                cur = con.cursor()
                cur.execute("SELECT shelfid,location FROM shelf")
                rows = cur.fetchall()
                for row in rows:
                    shelfid = row[0]
                    location= row[1]

                    #print(str(pid)+ " "+ pname)
                    t2=(str(shelfid),location)
                    l2.append(t2)
                
   locationlist=l2

