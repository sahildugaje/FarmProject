from flask import *
import mysql.connector
import re
import json
import datetime as dt
import uuid 

application = Flask(__name__)
application.secret_key = 'farmdetails565432134985'
application.jinja_env.add_extension('jinja2.ext.loopcontrols')


@application.route('/', methods=['GET', 'POST'])
def index():
	try:
		email = session.get('email', None)
		password = session.get('password', None)
		#print(email, password)
		
		mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com', database='FarmData', user='lecture', password='sahild1002')
		mycursor = mydb.cursor()
		mycursor.execute('SELECT numOfFarmStepStatus,nameOfFarmStepStatus,numOfFarm FROM user WHERE email ="'+email+'";')
		FarmStepStatus = mycursor.fetchone()
		numOfFarm = FarmStepStatus[2]
		#print("FarmStepStatus : ",FarmStepStatus)
		if(FarmStepStatus[0] != 1):
			return render_template('numberOfFarms.html')
		elif(FarmStepStatus[1] != 1):
			return render_template('selectfarm.html',data = int(numOfFarm))
		mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
		myresult = mycursor.fetchall()
		userId = myresult[0][2]
		mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id='''+str(userId)+''' ;''')
		farmIdAndName = mycursor.fetchall()
		mycursor.execute('SELECT pesticide_name FROM data;')
		pesticide = mycursor.fetchall()
		pesticideList =[]
		for pItems in pesticide:
			pesticideList.append(pItems[0])
	except:
		return render_template('signin.html')
	#try:
	mycursor.execute('SELECT d_pesticide_id,pesticide_name FROM data;')
	pesticideIdAndName = mycursor.fetchall()
	#print("pesticideIdAndName : ", pesticideIdAndName)
	farmIdList =[]
	quantity = []
	pesticideName = []
	unit = []
	if(email == myresult[0][0] and password == myresult[0][1]):
		if request.method == 'POST':
			farmD = request.form.to_dict()
			#return jsonify(farmD)
			for item in farmD:
				#print("item : ",item)
				if(item.isnumeric()):
					farmIdList.append(item)
				elif(re.findall("textbox", item)):
					pesticideName.append(farmD["textbox"+item[-1]])
				elif(re.findall("quantity",item)):
					quantity.append(farmD["quantity"+item[-1]])
				elif(re.findall("unit",item)):
					unit.append(farmD["unit"+item[-1]])
			#return jsonify(farmIdList,pesticideName,quantity,unit)
			totalPesticidesInDb = int(pesticideIdAndName[-1][0])
			j = 1
			for listEle in farmIdList:
				id = uuid.uuid1()
				i = 0
				for pesticideItem,u in zip(pesticideName,unit):

					for items in pesticideIdAndName:
						if (items[1] == pesticideItem):
							mycursor.execute('''INSERT INTO farm_pesticide_rel(f_farm_id,f_pesticide_id,pesticide_quantity,DATE,UUID,unit) VALUES(''' + str(listEle) + ''',''' + str(items[0]) + ''',''' + str(quantity[i]) + ''',convert_tz(NOW(),'+00:00','+05:30'),"'''+str(id)+'''","'''+str(u)+'''");''')
							mydb.commit()
							i = i + 1
							break
					else:
						addPesticide = totalPesticidesInDb + j
						mycursor.execute('INSERT INTO data(d_pesticide_id,pesticide_name) VALUES(' + str(addPesticide) + ',"' + str(pesticideItem) + '");')
						j = j + 1
						mydb.commit()
						mycursor.execute('''INSERT INTO farm_pesticide_rel(f_farm_id,f_pesticide_id,pesticide_quantity,DATE,UUID,unit) VALUES(''' + str(listEle) + ''',''' + str(addPesticide) + ''',''' + str(quantity[i]) + ''',convert_tz(NOW(),'+00:00','+05:30'),"'''+str(id)+'''","'''+str(u)+'''");''')
						mydb.commit()
						i = i + 1
			mycursor.execute('SELECT pesticide_name FROM data;')
			pesticide = mycursor.fetchall()
			pesticideList =[]
			for pItems in pesticide:
				pesticideList.append(pItems[0])
		return render_template("index.html",userId=int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList)
	else:
		return jsonify("Email Not Registered or Password Wrong")
	#except:
                #return '{} {}'.format("<script>alert('Error Occured Please try Again!')</script>", render_template('index.html',userId = int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList))

@application.route('/showFarmHistory', methods = ['GET','POST'])
def showFarmHistory():
	try:
		email = session.get('email',None)
		password = session.get('password',None)
		userId = session.get('userId',None)

		mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
				         database='FarmData',
				         user='lecture',
				         password='sahild1002')
		mycursor = mydb.cursor()
		mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id=''' + str(userId) + ''' ;''')
		farmIdAndName = mycursor.fetchall()

		mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="' + email + '";')
		myresult = mycursor.fetchall()

		if (email == myresult[0][0] and password == myresult[0][1]):
			return render_template("farmhistory.html",farmIdAndName=farmIdAndName)
		else:
			return render_template("signin.html")
	except :
		return jsonify("No data found")

@application.route('/showData', methods = ['GET','POST'])
def showData():
	#try:
	email = session.get('email',None)
	password = session.get('password',None)
	userId = session.get('userId',None)
	
	mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
	                         database='FarmData',
	                         user='lecture',
	                         password='sahild1002')
	mycursor = mydb.cursor()
	mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id=''' + str(userId) + ''' ;''')
	farmIdAndName = mycursor.fetchall()

	mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="' + email + '";')
	myresult = mycursor.fetchall()
	mycursor.execute('SELECT pesticide_name FROM data;')
	pesticide = mycursor.fetchall()
	pesticideList =[]
	for pItems in pesticide:
		pesticideList.append(pItems[0])
	if (email == myresult[0][0] and password == myresult[0][1]):
		if request.method == 'POST':
			farm = request.form['farm']
			session['farm'] = farm
			farmId = session.get('farm', None)

			mycursor.execute('''SELECT pesticide_name,DATE,pesticide_quantity,UUID,unit FROM user
					INNER JOIN user_farm_rel ON user_id = uf_user_id
					INNER JOIN farm ON farm_id = uf_farm_id
					INNER JOIN farm_pesticide_rel ON farm_id = f_farm_id
					INNER JOIN data ON f_pesticide_id = d_pesticide_id
					WHERE user_id =''' + str(userId) + ''' and farm_id = ''' + str(farmId) + ''' ORDER BY DATE ASC;''')
			data = mycursor.fetchall()
			#print(data)
			flag = 0
			listData =[]
			listDate = []
			listQuantity = []
			listUnit = []
			listData.append([data[0][0]])
			listDate.append([data[0][1]])
			listQuantity.append([data[0][2]])
			listUnit.append([data[0][4]])
			for i in range(0,len(data)-1):
				
				if((data[i][3] == data[i+1][3]) and flag == 0):
					j = len(listData)-1

					#listData.append([data[i][0]])
					listData[j].extend([data[i+1][0]])
					listDate[j].extend([data[i+1][1]])
					listQuantity[j].extend([data[i+1][2]])
					listUnit[j].extend([data[i+1][4]])
					flag = 1
					
				elif((data[i][3] == data[i+1][3]) and flag == 1):
					listData[j].extend([data[i+1][0]])
					listDate[j].extend([data[i+1][1]])
					listQuantity[j].extend([data[i+1][2]])
					listUnit[j].extend([data[i+1][4]])
				else:
					if(i == len(data)-1):
						listData.append([data[i][0]])
						listDate.append([data[i][1]])
						listQuantity.append([data[i][2]])
						listUnit.append([data[i][4]])
						break
					listData.append([data[i+1][0]])
					listDate.append([data[i+1][1]])
					listQuantity.append([data[i+1][2]])
					listUnit.append([data[i+1][4]])
					flag = 0
			#print("listUnit :",listUnit)
			return render_template('table.html', Data=zip(listData,listDate,listQuantity,listUnit),dataQuantityAndUnit=zip(listData,listQuantity,listUnit),zip=zip)
	else:
		return render_template("signin.html")
	#except:
		#return '{} {}'.format("<script>alert('No Data Found')</script>", render_template('index.html',userId = int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList))

	
@application.route('/signUpPage', methods = ['GET','POST'])
def signUpPage():
	return render_template ('signup.html')
	
@application.route('/signInPage', methods = ['GET','POST'])
def signInPage():
	try:
		email = session.get('email',None)
		password = session.get('password',None)
		if(email == None):
			return render_template('signin.html')
		mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
		mycursor = mydb.cursor()
		mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
		myresult = mycursor.fetchall()
		userId = myresult[0][2]
		if(myresult == []):
			return render_template('signin.html')
		mycursor.execute('SELECT pesticide_name,d_pesticide_id FROM data;')
		pesticideList = mycursor.fetchall() 
		if(email == myresult[0][0] and password == myresult[0][1]):
			mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id='''+str(userId)+''' ;''')
			farmIdAndName = mycursor.fetchall()
			return render_template("index.html",userId = int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList)
		else:
			return render_template('signin.html')
	except:
		return render_template('signin.html')
@application.route('/signUp', methods = ['POST'])
def signUp():
	try:
		if request.method == 'POST':
			email = request.form['email']
			password = request.form['password']
			#print(email)
			mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
			mycursor = mydb.cursor()
			mycursor.execute('INSERT INTO user(email,passw) VALUES("'+email+'","'+password+'");')
			mydb.commit()
			#print(email)
			mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
			myresult = mycursor.fetchall()
			userData = []
			userData = (str(myresult[0][2])+":"+str(myresult[0][1]))
			##print('USER DATA :',userData)
			session['email'] = email
			session['password'] = password
			#print('Myresult :',myresult)
			mycursor.execute('SELECT pesticide_name,d_pesticide_id FROM data;')
			pesticideList = mycursor.fetchall() 
			if(myresult == []):
				return("Email Not Registered or Wrong Password")
			if(myresult[0][0] == email and password == myresult[0][1]):
				userId = myresult[0][0]
				session['email'] = email
				session['password'] = password
				session['userId'] = myresult[0][2]
		return render_template('numberOfFarms.html')
	except:
		return jsonify('Email aldready Registered')

@application.route('/signin', methods = ['GET','POST'])	
def signin():
	#return 'SignIn'
	try:
		if request.method == 'POST':
			email = request.form['email']
			password = request.form['password']
			mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
			mycursor = mydb.cursor()
			mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
			myresult = mycursor.fetchall()
			userData = []
			userData = (str(myresult[0][2])+":"+str(myresult[0][1]))
			userId = str(myresult[0][2])
			#print('USER DATA :',userData)
			#print('email :',email)
			#print('myresult',myresult)
			mycursor.execute('SELECT pesticide_name,d_pesticide_id FROM data;')
			pesticide = mycursor.fetchall() 
			if(email == myresult[0][0] and password == myresult[0][1]):
				session['email'] = email
				session['password'] = password
				session['userId'] = str(myresult[0][2])
				mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id='''+str(userId)+''' ;''')
				farmIdAndName = mycursor.fetchall()
				mycursor.execute('SELECT pesticide_name FROM data;')
				pesticide = mycursor.fetchall()
				pesticideList =[]
				for pItems in pesticide:
					pesticideList.append(pItems[0])
				#print('pesticideList :',pesticideList)
				return render_template("index.html",userId = int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList)
			else:
				return("Email Not Registered or Wrong Password")
		return render_template("signUpInPage.html")
	except:
		return jsonify('You Dont Have Account!')


@application.route('/numberoffarms', methods = ['GET','POST'])
def numberoffarms():

	email = session.get('email',None)
	password = session.get('password',None)
	try:
		mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
		mycursor = mydb.cursor()
		mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
		myresult = mycursor.fetchall()
		if(myresult == []):
			return("Email Not Registered or Wrong Password")
		if request.method == 'POST':
			numOfFarm = request.form['numOfFarm']
			session['numOfFarm'] = numOfFarm
			#print('numOfFarm',numOfFarm)
			mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
			mycursor = mydb.cursor()
			mycursor.execute('UPDATE user SET numOfFarmStepStatus = 1, numOfFarm = '+str(numOfFarm)+' WHERE email = "'+str(email)+'";')
			mydb.commit()
		return render_template('selectfarm.html',data = int(numOfFarm))
	except:
		return jsonify('Invalid')

@application.route('/selectfarm', methods = ['GET','POST'])
def selectfarm():
	email = session.get('email',None)
	password = session.get('password',None)
	userId = session.get('userId',None)
	#print(userId)
	#try:
	mydb = mysql.connector.connect(host='lecture.cechxabyoyas.ap-south-1.rds.amazonaws.com',
                                         database='FarmData',
                                         user='lecture',
                                         password='sahild1002')
	mycursor = mydb.cursor()
	mycursor.execute('SELECT email,passw,user_id FROM user WHERE email ="'+email+'";')
	myresult = mycursor.fetchall()
	if(myresult[0][0] != email):
		return("Email Not Registered or Wrong Password")
	if request.method == 'POST':
		numOfFarm = session.get('numOfFarm', None)
		farm = []
		for i in range(0, int(numOfFarm)):
			farm.append(request.form[str(i)])
			i=i+1
		for items in farm:
			#print(items)
			mycursor.execute('INSERT INTO farm(farm_name) VALUES("'+str(items)+'");')
			mydb.commit()
			mycursor.execute('SELECT farm_id FROM farm')
			result_farm = mycursor.fetchall()
			farmId = result_farm[-1][0]
			#print(result_farm)
			#print('farm id:',farmId)
			#print('user id:',userId)
			mycursor.execute('INSERT INTO user_farm_rel(uf_farm_id,uf_user_id) VALUES ('+str(farmId)+','+str(userId)+');')
			mydb.commit()	
			mycursor.execute('UPDATE user SET nameOfFarmStepStatus = 1 WHERE email = "'+str(email)+'";')
			mydb.commit()
	mycursor.execute('SELECT pesticide_name,d_pesticide_id FROM data;')
	pesticideList = mycursor.fetchall() 
	mycursor.execute('''SELECT farm_id,farm_name FROM user_farm_rel INNER JOIN farm ON uf_farm_id = farm_id WHERE uf_user_id='''+str(userId)+''' ;''')
	farmIdAndName = mycursor.fetchall()
	return render_template("index.html",userId = int(userId),farmIdAndName=farmIdAndName,pesticideList=pesticideList)
	#except e as exception: 
	#	return jsonify(e)

@application.route('/logOut', methods = ['GET','POST'])
def logOut():
	if request.method == 'POST' or request.method == 'GET':
		session.clear()
		return render_template("signin.html")
@application.route('/downloadPDF', methods = ['GET'])
def downloadPDF():
	if request.method == 'GET':
	# with open("outputs/Adjacency.csv") as fp:
	#     csv = fp.read()
		csv = '1,2,3\n4,5,6\n'
		return Response(
		csv,
		mimetype="text/csv",
		headers={"Content-disposition":
		         "attachment; filename=myplot.csv"})

if (__name__ == "__main__"):
	application.run(host='0.0.0.0',port=5000, debug = True)
