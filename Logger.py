import logging

class Logger:
	def __init__(self, log_location):
		self.logger = logging.getLogger('myapp')
		hdlr = logging.FileHandler(log_location)
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		hdlr.setFormatter(formatter)
		self.logger.addHandler(hdlr)
		self.logger.setLevel(logging.DEBUG)

	def write_info(self, message):
		self.logger.info(message)
		
	def write_warning(self, message):
		self.logger.warn(message)
	
	def write_error(self, message):
		self.logger.error(message)	
	