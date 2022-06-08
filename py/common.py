import enum
import math

class Building:
	def __init__(self, name):
		"""
		rooms: dict str->Room
		:param name: str
		"""
		self.name = name
		self.rooms = dict()
	def __repr__(self):
		return f"Building {self.name}"

class Room:
	# 부드러우라고 list 아닌 dict 씀.
	DAYMAP = {
		0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"
	}
	def __init__(self, name):
		"""
		uses: [Use]
		:param name: str
		"""
		self.name = name
		self.uses = list()
	def __repr__(self):
		return f"Room {self.name}"
	def calcblocks(self, d, extrauses, blocksize, startsec, endsec):
		"""
		:param d: date
		:param extrauses: [Use]
		:param startsec: int, (초)
		:param endsec: int, (초)
		:param blocksize: int, 도막 크기(초)
		"""
		alluses = self.uses + extrauses
		weekday = Room.DAYMAP[d.weekday()]
		blocks = [0] * math.ceil((endsec - startsec) / blocksize)
		for u in filter(lambda x: x.startdate <= d and d <= x.enddate, alluses):
			for t in filter(lambda x: x.recurrence == weekday or x.recurrence == "날", u.times):
				bstart = blockidxfloor(totalsec(t.start), startsec, blocksize, len(blocks))
				bend = clamp(math.ceil((totalsec(t.end) - startsec) / blocksize), 0, len(blocks))
				blocks[bstart:bend] = [x + u.size for x in blocks[bstart:bend]]
		return blocks

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

def totalsec(d):
	return d.hour * 3600 + d.minute * 60 + d.second

def clamp(val, minv, maxv):
	return max(minv, min(val, maxv))

def blockidxfloor(cursec, startsec, blocksize, numblocks):
	return clamp((cursec - startsec) // blocksize, 0, numblocks)
