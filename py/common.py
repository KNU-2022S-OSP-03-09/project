import enum

class Building:
	def __init__(self, name):
		"""
		:param name: str
		"""
		self.name = name
		self.rooms = dict()

class Room:
	def __init__(self, name):
		"""
		uses: [Use]
		:param name: str
		"""
		self.name = name
		self.uses = list()

class Use:
	def __init__(self, size, startdate, enddate, times, name=None):
		"""
		강의 따위
		:param size: int, 크기(사람 수)
		:param startdate:
		:param enddate:
		:param times: [Time]
		:param name: str
		"""
		self.size = size
		self.startdate = startdate
		self.enddate = enddate
		self.times = times
		self.name = name

class Recurrence(enum.Enum):
	MONDAY = 0
	TUESDAY = 1
	WEDNESDAY = 2
	THURSDAY = 3
	FRIDAY = 4
	SATURDAY = 5
	SUNDAY = 6
	EVERYDAY = 100

class Time:
	def __init__(self, start, length, recurrence):
		"""
		하루 안의 이어진 시간
		:param start: int, 0시부터 센 분
		:param length: int, 분
		:param recurrence: Recurrence
		"""
		self.start = start
		self.length = length
		self.recurrence = recurrence

class User:
	def __init__(self, name, num, uses):
		"""
		:param name: str
		:param num: int
		:param uses: [Use]
		"""
		self.name = name
		self.num = num
		self.uses = uses
