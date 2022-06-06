import enum

class Building:
	def __init__(self, name):
		"""
		rooms: dict str->Room
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
	BLOCKING_SIZE = 99999999
	def __init__(self, size, startdate, enddate, times, name=None):
		"""
		강의 따위
		:param size: int, 크기(사람 수)
		:param startdate: date
		:param enddate: date, 닫힘
		:param times: [Time]
		:param name: str
		"""
		self.size = size
		self.startdate = startdate
		self.enddate = enddate
		self.times = times
		self.name = name
	def __repr__(self):
		return f"Use {self.name}, {self.size} {self.startdate} - {self.enddate} {self.times}"

class Time:
	def __init__(self, start, end, recurrence):
		"""
		하루 안의 이어진 시간
		:param start: time
		:param end: time
		:param recurrence: str '월' '화' '수' '목' '금' '토' '일' '날' 가운데 하나
		"""
		self.start = start
		self.end = end
		self.recurrence = recurrence
	def __repr__(self):
		return f"Time {self.start} {self.end} {self.recurrence}"
