from flask import Flask,render_template,url_for,redirect,request
import sqlite3

from forms import LoginForm,UpdateForm,RemoveForm,ViewForm,LogoutForm,ShoppingListForm
from datetime import datetime,timedelta
app = Flask(__name__)
app.secret_key='development key'
currentuser=''



def validatelogin(username, password):
		con = sqlite3.connect('refrigerator.db')
		dbUser=username
		completion = False
		with con:
								cur = con.cursor()
								cur.execute("SELECT password FROM user WHERE userid=?",(dbUser,))
								row = cur.fetchone()
								if row is not None:
										dbPass=row[0]

										print(dbUser+ " "+ dbPass)
										if dbPass==password:
											completion=True
															
		return completion


@app.route('/', methods=['GET', 'POST'])
def login():
			 error = None
			 form = LoginForm()

			 if form.validate_on_submit():
				 username=form.username.data
				 password=form.password.data
				 completion= validatelogin(username, password)
				 if completion ==False:
						error = 'Invalid Credentials. Please try again.'
				 else:
						global currentuser 
						currentuser=username
						print(currentuser+ " in login")
						return redirect(url_for('home'))
				
			 return render_template('login.html', error=error,form=form)

def addfunction(productid,shelfid,quantity):
	con = sqlite3.connect('refrigerator.db')
	error=0 #no error
	
	with con:
								cur = con.cursor()
								global currentuser 
								days=0
								cur.execute("SELECT * FROM current_contents WHERE userid=? AND itemid=? ",(currentuser,productid))
								rows = cur.fetchall()
								if rows:
									error=1 #already exists in that shelf
								else:
									cur.execute("SELECT templow, temphigh,expiryperiod from products WHERE productid=?",(productid,))
									row=cur.fetchone()
									pl=row[0]
									ph=row[1]
									days=row[2]
									cur.execute("SELECT templo, temphi from shelf WHERE shelfid=?",(shelfid,))
									row=cur.fetchone()
									sl=row[0]
									sh=row[1]
									if(pl>sh or ph<sl):
										error=2 #unsuitable temperature
									else:
										cur.execute('SELECT itemid from shoppinglist where why=0 AND userid= ? AND itemid=?', (currentuser,productid))
										rows2=cur.fetchone()
										if rows2 is not None:
											cur.execute("DELETE FROM shoppinglist where userid=? and itemid=?",(currentuser,productid))




										cur.execute('DROP TRIGGER t1')
										cur.execute('''CREATE TRIGGER t1
											AFTER INSERT ON current_contents
											BEGIN
												INSERT INTO logmanager VALUES (new.userid,new.itemid,strftime('%s','now'),'INSERTION');
											END;
											''')




										now=datetime.now().date()
										print(now)
										expiry=now+timedelta(days=days)
										print(expiry)
										print(currentuser + " in add")
										cur.execute("INSERT INTO current_contents VALUES (?, ?, ? , ?,?) ",(currentuser,productid,shelfid,quantity,expiry))
													   
	return error

def removefunction(productid,quantity):
	con = sqlite3.connect('refrigerator.db')
	error=0 #no error
	row=None
	with con:
								cur = con.cursor()
								global currentuser
								cur.execute("SELECT quantity FROM current_contents WHERE userid=? AND itemid=? ",(currentuser,productid))
								row = cur.fetchone()
								if row is None:
									error=1 #product does not exist in the refrigerator
								else:
									ipqty=quantity
									availableqty=row[0]
									if(ipqty>availableqty):
										error=2 #insufficient quantity in fridge
									else:
										newqty=availableqty-ipqty
										cur.execute('DROP TRIGGER t2')
										cur.execute('''CREATE TRIGGER t2
											AFTER UPDATE ON current_contents
											BEGIN
												INSERT INTO logmanager VALUES (old.userid,old.itemid,strftime('%s','now'),'REMOVED');
											END;
											''')

										cur.execute("UPDATE current_contents SET quantity=? WHERE userid=? AND itemid=? ",(newqty,currentuser,productid))
										if(newqty==0):
											################UPDATE SHOPPING LIST HERE- INSERT INTO SHOPPING_LIST TABLE WITH (QUANTITY==0) WALA VARIABLE AS 1 #####################
											why=0 #for qty=0
											cur.execute("INSERT INTO shoppinglist VALUES (?,?,?)",(currentuser,productid,why))
											cur.execute("DELETE FROM current_contents WHERE userid=? AND itemid=?", (currentuser,productid) )

									
	return error




@app.route('/home',  methods=['GET', 'POST'])
def home():
	global currentuser
	user=currentuser
	form=LogoutForm()
	if form.validate_on_submit():
		currentuser=''
		return redirect(url_for('login'))
	return render_template('index.html' , form=form,user=user)
		




@app.route('/view-content', methods=['GET', 'POST'])
def view_content():
	form=ViewForm()
	rows=[]
	
	if form.validate_on_submit():
		con = sqlite3.connect( 'refrigerator.db' )
		print(form.what_to_display.data)	
		print("choice made ^")

		if(form.what_to_display.data=='1'):
				print("inside if 1")
				with con:
					cur = con.cursor()
					cur.execute("SELECT productname,categoryname,location,quantity,expirydate FROM current_contents , products, shelf,category WHERE userid=? AND itemid=productid AND current_contents.shelfid=shelf.shelfid AND category.categoryid=products.categoryid ", (currentuser,)) 
					# ^add expiry date after quantity 
					rows = cur.fetchall()

		elif(form.what_to_display.data=='2'):
			
				with con:
					cur = con.cursor()
					cur.execute("SELECT location,productname,categoryname,quantity,expirydate FROM current_contents , products, shelf,category WHERE userid=? AND itemid=productid AND current_contents.shelfid=shelf.shelfid AND category.categoryid=products.categoryid GROUP BY location, productname,categoryname,quantity,expirydate ORDER BY location", (currentuser,)) 
					# ^add expiry date after quantity 
					rows = cur.fetchall()

		elif(form.what_to_display.data=='3'):
			
				with con:
					cur = con.cursor()
					cur.execute("SELECT categoryname,productname,location,quantity,expirydate FROM current_contents , products, shelf,category WHERE userid=? AND itemid=productid AND current_contents.shelfid=shelf.shelfid AND category.categoryid=products.categoryid GROUP BY categoryname, productname,location,quantity,expirydate ORDER BY categoryname", (currentuser,)) 
					# ^add expiry date after quantity 
					rows = cur.fetchall()
		else:
			with con:
				cur = con.cursor()
				cur.execute("SELECT expirydate,productname,categoryname,location,quantity FROM current_contents , products, shelf,category WHERE userid=? AND itemid=productid AND current_contents.shelfid=shelf.shelfid AND category.categoryid=products.categoryid  GROUP BY expirydate,productname,categoryname,location,quantity ORDER BY expirydate", (currentuser,))
				rows=cur.fetchall()
		return render_template('view_content.html',form=form,rows=rows,table=form.what_to_display.data)
	return render_template('view_content.html',form=form,rows=rows,table=form.what_to_display.data)





@app.route('/update', methods=['GET', 'POST'])
def update():
	form=UpdateForm()
	message=''
	if form.validate_on_submit():
				productid=form.productname.data 
				#stores productid(201) of the selected product(milk) 
				#milk is displayed in the dropdown but the value selected is its productid
				shelfid=form.location.data #stores shelfid 
				quantity=form.quantity.data
				 
				error=addfunction(productid,shelfid,quantity)
				if(error==0):
					message='Successfully Added'
				elif(error==1):
					message="You already have this item in the refrigerator. Please try another item."
				elif(error==2):
					message="This item should be placed in another shelf with suitable temperature range. Please try another location."

				return render_template('update.html',message=message,form=form)

	return render_template('update.html',message=message, form=form)


@app.route('/remove', methods=['GET', 'POST'])
def remove():
	form=RemoveForm()
	message=''
	if form.validate_on_submit():
				 productid=form.productname.data 
				 #stores productid(201) of the selected product(milk) 
				 #milk is displayed in the dropdown but the value selected is its productid
				
				 quantity=form.quantity.data
				 error=removefunction(productid,quantity)
				 if (error==0):
						message='Successfully Removed'
				 elif(error==1):
						message="The selected item does not exist in the refrigerator. Please try another item."
				 elif(error==2):
						message="Insufficient Quantity. Please select suitable quantity."

				 return render_template('remove.html',message=message,form=form)

	return render_template('remove.html',message=message, form=form)

@app.route('/shopping-list', methods=['GET', 'POST'])
def shopping_list():
	form=ShoppingListForm()
	rows=[]
	type_=''
	if form.validate_on_submit():
		type_=form.x.data
		con = sqlite3.connect( 'refrigerator.db' )
		
		global currentuser
		if(type_=='0'):
			with con:
				cur=con.cursor()
				cur.execute('SELECT productname FROM shoppinglist,products WHERE itemid=productid AND userid=? AND why=0 ',(currentuser,))
				rows=cur.fetchall()
		if(type_=='1'):
			now=datetime.now().date()
			days=2
			now=now+timedelta(days=days)
			print(now)
			with con:
				cur=con.cursor()

				cur.execute('DELETE FROM shoppinglist WHERE userid=? AND why=1', (currentuser,))
				cur.execute('SELECT itemid FROM current_contents where userid= ? AND expirydate <=?',(currentuser,now))
				rows2=cur.fetchall()
				for row in rows2:
					itemid=row[0]
					x=1
					cur.execute('INSERT INTO shoppinglist VALUES (?,?,?)',(currentuser,itemid,x))
			
				cur.execute('SELECT productname FROM shoppinglist,products WHERE itemid=productid AND userid=? AND why=1 ',(currentuser,))			
				rows=cur.fetchall()



	return render_template('shopping_list.html',form=form,rows=rows,type_=type_)



@app.route('/refrigerator-settings')
def refrigerator_settings():
	con = sqlite3.connect( 'refrigerator.db' )
	with con:
					cur = con.cursor()
					cur.execute("SELECT location,templo,temphi FROM shelf")
					rows=cur.fetchall()
	return render_template('refrigerator_settings.html',rows=rows)




if __name__ == '__main__':
	app.run(debug=True)

