import json
import requests
import datetime
import time as t
from datetime import datetime, timedelta
import sqlite3
import sys
from requests.exceptions import ConnectionError
import psycopg2

number_terminals = 3

terminals = ['http://192.168.100.23:8090', 'http://192.168.100.26:8090','http://192.168.100.21:8090']

delay = 20 #records are requested for this time interval

c_cloud_update = 0 #counter for update cloud bd

while True:

	start_time = datetime.now() - timedelta(seconds=delay)
	stop_time = datetime.now() 
	local_bd = sqlite3.connect("db.sqlite3") # Open local database
	try:	
#		cloud_bd = psycopg2.connect(dbname='database', user='db_user', password='mypassword', host='localhost')
		cloud_bd = sqlite3.connect("db_cloud.sqlite3")
	except:
		c_cloud_update=c_cloud_update+1
	
	# Aligning the new time to the format for the terminal
	
	start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
	stop_time = stop_time.strftime('%Y-%m-%d %H:%M:%S')
	print(start_time)
	print(stop_time)
		
	# Creating an executable command for all terminals
	
	for n in range (number_terminals):
		
		terminal = terminals[n]	
		
		try:
			comm_passtime = "/newFindRecords?pass=12345678&length=-1&personId=-1&index=0&startTime=" + start_time + "&endTime=" + stop_time + "&model=-1"
			url_passtime = terminal + comm_passtime
			find_passtime = requests.get(url_passtime, timeout=1) 	#request to terminal
			a = find_passtime.json()					#reply from terminal in JSON format
			records = a['data']['records']
			total = a['data']['pageInfo']['total']
			
			# For all new records:
					
			for a in range(total):
				print(records[a]['id'])
				
			# Converting time from UNIX to normal
				
				d = (records[a]['time'])/1000		
				time_pass = datetime.utcfromtimestamp(d) - timedelta(hours=5)
				print(time_pass)
				
			# Get child Id	
				
				person_id = str(records[a]['personId'])
				print(person_id)
				status = records[a]['type']
				print(status)
			
			# Get child name
			
				with local_bd:
					cur = local_bd.cursor()
					cur.execute("SELECT child_name FROM id_id WHERE id_child=?", (person_id,))
					child_name = cur.fetchone()
					print(child_name[0])
				
			#Checking pass permission (0 - yes, 1 - no)
			
				if status == 0:
					
				# Retrieving information from a database of name and updating passing time 	
					
					with local_bd:
						cursor = local_bd.cursor()
						cursor.execute("UPDATE id_id SET enter_date=? WHERE id_child=?", (time_pass, person_id,))
						cursor.close()
						local_bd.commit()
						local_bd.close()
					try:
						with cloud_bd:
							cursor = cloud_bd.cursor()
							cursor.execute("UPDATE id_id SET enter_date=? WHERE id_child=?", (time_pass, person_id,))
							cursor.close()
							cloud_bd.commit()
							cloud_bd.close()
					except:
						pass
				
						
				else:
					pass

				
		except ConnectionError:
			pass
		
	# Executable command in the cloud to update
		
	t.sleep(20)
	
