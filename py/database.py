import datetime

import sqlalchemy
from sqlalchemy import create_engine, text

from common import Use, Time

DBP = {
	"url": ["sqlite+pysqlite:///db/edbn.db", "postgresql+psycopg2://localhost:5432/edbn"],
	#"idt": ["INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY"],
	"timew": [lambda x: x.isoformat(), lambda x: x],
	"timer": [datetime.time.fromisoformat, lambda x: x],
	"datew": [lambda x: x.isoformat(), lambda x: x],
	"dater": [datetime.date.fromisoformat, lambda x: x]
}
DBMS = 0

engine = create_engine(DBP["url"][DBMS])

def create():
	commands = [
		f"CREATE TABLE buildings (name VARCHAR(80) PRIMARY KEY);",
		f"CREATE TABLE rooms (name VARCHAR(80), building_name VARCHAR(80) NOT NULL REFERENCES buildings(name), PRIMARY KEY(name, building_name));",
		f"CREATE TABLE users (studentnum INTEGER PRIMARY KEY, name VARCHAR(160));",
		"""CREATE TABLE uses (
			name VARCHAR(160),
			size INTEGER NOT NULL,
			startdate DATE NOT NULL,
			starttime TIME NOT NULL,
			endtime TIME NOT NULL,
			building_name VARCHAR(80) NOT NULL,
			room_name VARCHAR(80) NOT NULL,
			usernum INTEGER REFERENCES users(studentnum),
			FOREIGN KEY (building_name, room_name) REFERENCES rooms(building_name, name)
		);""",
		"CREATE INDEX uses_brd_index ON uses (building_name, room_name, startdate);"
		#"CREATE INDEX uses_date_index ON uses (startdate);"
	]
	with engine.begin() as conn:
		for c in commands:
			conn.execute(text(c))

def populate(buildings):
	"""
	:param buildings: [Building]
	"""
	binsert = text("INSERT INTO buildings (name) VALUES (:name);")
	rinsert = text("INSERT INTO rooms (building_name, name) VALUES (:bn, :name);")
	with engine.begin() as conn:
		conn.execute(binsert, [vars(x) for x in buildings])
		for b in buildings:
			#conn.execute(text("INSERT INTO rooms (building_name, name) VALUES (:bn, :name)"), [vars(x), "bn": b.name for x in b.rooms.values()])
			for r in b.rooms.values():
				conn.execute(rinsert, bn=b.name, name=r.name)

def insertuse(building, room, use, studentnum):
	"""Time이 하나뿐이고 startdate == enddate인 Use만 들어감."""
	command = text("INSERT INTO uses (name, size, startdate, starttime, endtime, building_name, room_name, usernum) VALUES (:name, :size, :startdate, :starttime, :endtime, :building_name, :room_name, :num);")
	with engine.begin() as conn:
		conn.execute(command, name=use.name, size=use.size,
				startdate=DBP["datew"][DBMS](use.startdate),
				starttime=DBP["timew"][DBMS](use.times[0].start),
				endtime=DBP["timew"][DBMS](use.times[0].end),
				building_name=building.name, room_name=room.name, num=studentnum)

def insertuser(name, studentnum):
	command = text("INSERT INTO users (name, studentnum) VALUES (:name, :studentnum);")
	with engine.begin() as conn:
		conn.execute(command, name=name, studentnum=studentnum)

def queryuses(building, room, startdate):
	"""
	:param building: Building
	:param room: Room
	"""
	command = text("SELECT name, size, starttime, endtime FROM uses WHERE building_name = :b and room_name = :r and startdate = :d;")
	with engine.begin() as conn:
		result = conn.execute(command, b=building.name, r=room.name, d=DBP["datew"][DBMS](startdate))
		return [Use(u[1], startdate, startdate, [Time(DBP["timer"][DBMS](u[2]), DBP["timer"][DBMS](u[3]), "날")], u[0]) for u in result]

def clearuses(beforedate):
	command = text("DELETE FROM uses WHERE startdate < :bd")
	with engine.begin() as conn:
		conn.execute(command, bd=DBP["datew"][DBMS](beforedate))

def resetdb():
	drops = ["DROP TABLE uses;", "DROP TABLE users;", "DROP TABLE rooms;", "DROP TABLE buildings;"]
	with engine.connect() as conn:
		for d in drops:
			try:
				conn.execute(text(d))
			except (sqlalchemy.exc.OperationalError, sqlalchemy.exc.ProgrammingError):
				pass
	create()
