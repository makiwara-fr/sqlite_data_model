# -*- coding: utf-8 -*-
# ###################################################################################
#
# 			Maintaining a SQLite database and ease the integration
#
#	License:
#	Author: 
#
#	                __   .__                              
#	  _____ _____  |  | _|__|_  _  _______ ____________   
#	 /     \\__  \ |  |/ /  \ \/ \/ /\__  \\_  __ \__  \  
#	|  Y Y  \/ __ \|    <|  |\     /  / __ \|  | \// __ \_
#	|__|_|  (____  /__|_ \__| \/\_/  (____  /__|  (____  /
#	      \/     \/     \/                \/           \/ 
#
# ###################################################################################



from sqlite3 import *
import os
import inspect
import json
from settings import log as log

class Database():
	""" class to handle a sqlite database  """
	def __init__(self, name, debug = True):
		# Connect to an access database using pyodbc
		self.debug = debug
		self.dbname = name
		log("Database : " + self.dbname + " created")

	def __del__(self):
		""" disconnect properly from database """
		self.disconnect()

	def connect(self):
		""" connect to a database """
		if (self.debug):
			print("Connecting to " + os.path.abspath(self.dbname))
		try:
			#Try to connect to db
			self.cnx = connect(os.path.abspath(self.dbname))
			print("Connection to db " + self.dbname + " successfull")

		except:
			print("Connection to db " + self.dbname + " failed")

	def disconnect(self):
		""" disconnect from a database """
		try:
			self.cnx.close()
			print("Connection to database " + self.dbname + " closed")
		except:
			pass


	def execute_query(self, query):
		"""retrieve values within db return a list containing all the informations """
		try:
			cursor = self.cnx.cursor()
			#execute the SQL change
			if self.debug == True:
				print("Executing following SQL command : " + query + " on db :" + self.dbname)
			lines = cursor.execute(query)
			data = cursor.fetchall()
			return data
		except:
			if self.debug == True:
				print("Error executing : " + query + " on db :" + self.dbname)
			return "Error"


	def commit_query(self, SQLquery):
		""" Commiting change a SQL query"""
		try:
			cursor = self.cnx.cursor()
			#execute the SQL change
			if self.debug == True:
				print("Executing following SQL command : " + SQLquery + " on db : " + self.dbname)
			cursor.execute(SQLquery)
			#commit change in db
			self.cnx.commit()
			return 0
		except:
			self.cnx.rollback()
			if self.debug == True:
				print("Error executing : " + SQLquery + " on db : " + self.dbname)
			return 1

	def define_function(self, function_name, function):
		""" include function inside the database to perform specific operation"""
		""" need positional argument in function only """
		self.cnx.create_function(function_name, len(inspect.signature(function).parameters), function)
		
	def read_table_lists(self):
		""" Find all the tables present in the database """
		""" return the results within a table """
		
		return self.execute_query("SELECT name FROM sqlite_master WHERE type='table';") 
		
	def read_table_structure(self, table_name):
		""" retrieve all information about the fields within a specified table """
		return self.execute_query("PRAGMA table_info(" + table_name + ");")
		
	def __create_join_sql(self, join_query, table_list, parameters_matrix):
		""" retrieve the code for an inner join of the list of tables define in table_list thanks to the joint of the parameters present in parameter_matrix """
		""" e.g. table_list = ["TABLE_1", "TABLE_2"] """
		""" 	parameters_matrix = [["Field 1 A", "Field 2 A"], ["Field 1 B", Field 2 C"]] """
		""" number of colums of matrix must equal the lenght of table list """
		
		# check data consistency
		number_of_tables = len(table_list)
		consistency = True
		
		# check if each line of the matrix has the same size than the table list
		for i, r in enumerate(parameters_matrix):
			if len(parameters_matrix[i]) != number_of_tables:
				consistency = False
			
		if consistency == True and number_of_tables > 0:
			
			sql = " SELECT * FROM "
			
			# declaration of tables to join
			for i, t in enumerate(table_list):
				if i < number_of_tables - 1:
					sql = sql + t + " " + join_query + " "
				else:
					sql = sql + t + " ON (" 
			
			# declaration of fields to be joint
			for j, r in enumerate(parameters_matrix):
				# look at one row
				for i in range(number_of_tables - 1):
					sql = sql + table_list[i] + "." + r[i] + " = "
				# close the statement for one row
				sql = sql + table_list[number_of_tables - 1] + "." + r[number_of_tables - 1]
				if j < len(parameters_matrix) - 1:
					sql = sql + " AND "
				
			#closing the phrase for all the rows
			sql = sql + ");"
			
			return sql
		else:
			if (self.debug == True):
				print("terminated due to bad parameters for creating join")
			return "ERROR"
		
	
	def create_inner_join(self, table_list, parameters_matrix):
		""" doc to be made """
		return self.__create_join_sql("INNER JOIN", table_list, parameters_matrix)
	
	###########################################################
	#
	#
	# creating the database based on model
	#
	#
	############################################################
	
	
	MODEL_TO_SQLITE = {
		"integer" : "INTEGER",
		"string": "TEXT",
		"time": "TEXT",
		"date": "TEXT",
		"float" : "REAL"
	}
	
	
	def define_model(self, json_model_file):
		""" define table according to data model describe in a json file"""
		try:
			with open(json_model_file) as model_file:
				model = json.load(model_file)
			sql = ""
			
			print(type(model))
			
			if type(model) == type([]):
				# we have alist
				for el in model:
					#iterate through the list
					sql = sql + " " + self._create_table(el)
			else:
				# unit table
				self._create_table(model)
		
			return sql
		except:
			return "error"
		
		
	
	
	
	def _create_model(self, format_dict, prefix = ""):
		""" generating a sql sequence to create the spefic fields for a table based on a model 
			it should not be called by something else than itself or _create_table """
		try:
			sql = ""
			for k,v in format_dict.items():
				if type(v) != list:
					# Value is a single element with can extract the model
					
					# Complete previous element with comma or not
					if sql == "":
						comma = ""
					else:
						comma = ","
					sql = sql + comma + " " 
					
					# add a prefix when we are actually called recursively
					if prefix != "":
						sql = sql + prefix + "_"
					# add the actual info as upper case
					sql = sql + k.upper() + " " + self.MODEL_TO_SQLITE[v.lower()]
					if k == "id":
						# We have a primary key
						sql = sql + " PRIMARY KEY"
				else:
					# we have a list so we will add the elements in the list with the prefix given by the current parent element
					for el in v:
						sql = sql + self._create_model(el, prefix = k.upper())
						
			return sql
		except Exception as e:
			log("Error in " + str(e) )
			return ""
	
	def _create_table(self, table_dict):
		""" generating a sql sequence to create a sqlite table"""
		try:
			if table_dict['type'] == "table":
				return "CREATE TABLE " + table_dict['name'] + "(" + self._create_model(table_dict['model']) + ");"
			else:
				# Error in formatting. Do nothing
				return ""
		except:
			return ""
