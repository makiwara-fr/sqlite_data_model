# -*- coding: utf-8 -*-

# ##########################
#
# 			settings
#
# ##########################
import logging

debug = True



DEFAULT_EXPORT_PATH = "./output/"
DEFAULT_INPUT_PATH ="./input/"


def log(str, level="info"):
	
	if level == "info":
		print(str)
		logging.info(str)
	else:
		if debug: 
			print(str)
		if level == "debug":
			logging.debug(str)
		elif level == "error":
			logging.error(str)
		else:
			logging.info(str)
	
