import datetime
import functools
import itertools
import json
import math
import sys

import apscheduler.schedulers.background
import flask

import common
import crawl
import database
import processraw



BLOCK_SIZE = 30 * 60
OPEN_SECOND = 9 * 60 * 60
CLOSE_SECOND = 18 * 60 * 60
BLOCK_STRINGS = [f"{(OPEN_SECOND + BLOCK_SIZE * i) // 3600:02}:{(OPEN_SECOND + BLOCK_SIZE * i) % 3600 // 60:02}" for i in range(math.ceil((CLOSE_SECOND - OPEN_SECOND) / BLOCK_SIZE))]
# datetime.time에 더할 수만 있었어도
USE_TIME_STRINGS = [f"{(OPEN_SECOND + BLOCK_SIZE * i) // 3600:02}:{(OPEN_SECOND + BLOCK_SIZE * i) % 3600 // 60:02}" for i in range(math.ceil((CLOSE_SECOND - OPEN_SECOND) / BLOCK_SIZE) + 1)]
ROOM_COLOR_CAP = 40

try:
	with open("raw/lectures.json", encoding="utf-8") as f:
		bldginfo = processraw.process(json.load(f))
except FileNotFoundError:
	crawl_yesno_answer = input("강의 데이터가 없습니다. 긁을까요?(yes-예/no-아니요): ").lower()
	if crawl_yesno_answer == "yes" or crawl_yesno_answer == "예":
		bldginfo = processraw.process(crawl.crawl_and_save())
	else:
		sys.exit()

app = flask.Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

scheduler = apscheduler.schedulers.background.BackgroundScheduler()
scheduler.start()



@scheduler.scheduled_job(trigger="cron", hour=0, minute=30)
def clearuses():
	database.clearuses(datetime.date.today())

@app.route("/")
def root():
	roompage = "rooms" if flask.request.args.get("noov") == "true" else "roomov"
	return flask.render_template("root.html", buildings=sorted(list(bldginfo)), roompage=roompage)

@app.route("/rooms/<building>")
def rooms(building):
	try:
		bldg = bldginfo[building]
	except KeyError:
		return flask.render_template("error.html", error=f"'{building}'(이)라는 건물이 없습니다")

	floors = dict()
	for i in bldg.rooms:
		if i[0] not in floors:
			floors[i[0]] = [i]
		else:
			floors[i[0]].append(i)
	floors = sorted(floors.items(), key=lambda x: '/' if x[0] == 'B' else x[0], reverse=True)
	floors = [(f, sorted(r)) for f, r in floors]
	return flask.render_template("rooms.html", building=building, floors=floors)

@app.route("/roomov/<building>")
def roomov(building):
	try:
		bldg = bldginfo[building]
	except KeyError:
		return flask.render_template("error.html", error=f"'{building}'(이)라는 건물이 없습니다")

	floors = dict()
	for i in bldg.rooms:
		if i[0] not in floors:
			floors[i[0]] = [i]
		else:
			floors[i[0]].append(i)
	floors = sorted(floors.items(), key=lambda x: '/' if x[0] == 'B' else x[0], reverse=True)
	floors = [[f, sorted(r)] for f, r in floors]

	today = datetime.date.today()
	nowdt = datetime.datetime.now()
	nowindex = common.blockidxfloor(nowdt.hour * 3600 + nowdt.minute * 60, OPEN_SECOND, BLOCK_SIZE, len(BLOCK_STRINGS))
	for i in range(len(floors)):
		for j in range(len(floors[i][1])):
			# 시렁할까?
			blocks = bldg.rooms[floors[i][1][j]].calcblocks(today, [], BLOCK_SIZE, OPEN_SECOND, CLOSE_SECOND)
			floors[i][1][j] = (floors[i][1][j], [calchue(b) if b < common.Use.BLOCKING_SIZE else b for b in blocks[nowindex:nowindex + 6]])
	return flask.render_template("roomov.html", building=building, floors=floors)

@app.route("/use/<building>/<room>")
def use(building, room):
	try:
		bldg = bldginfo[building]
		rm = bldg.rooms[room]
	except KeyError:
		return flask.render_template("error.html", error=f"'{building} {room}'(이)라는 방이 없습니다")

	targetdate = datetime.date.today()
	dateblocks = [None] * 5
	datenames = [None] * 5
	for i in range(7):
		if targetdate.weekday() < 5:
			useruses = database.queryuses(bldg, rm, targetdate)
			dateblocks[targetdate.weekday()] = rm.calcblocks(targetdate, useruses, BLOCK_SIZE, OPEN_SECOND, CLOSE_SECOND)
			datenames[targetdate.weekday()] = targetdate.isoformat()[5:]
		targetdate += datetime.timedelta(days=1)
	hues = {p: calchue(p) for p in itertools.chain(*dateblocks)}
	dateblocks = list(map(list, zip(*dateblocks)))
	return flask.render_template("use.html", building=building, room=room, dates=datenames, times=BLOCK_STRINGS, blocks=dateblocks, hues=hues)

# 굳혀야함(fill, checkerrors)
@app.route("/fill", methods=["POST"])
def fill():
	data = dict(flask.request.form)
	stnum = data["studentnum"]
	name = data["name"]
	building = data["building"]
	room = data["room"]
	del data["studentnum"]
	del data["name"]
	del data["building"]
	del data["room"]
	error = checkerrors(stnum, data)
	if error is None:
		blocks = [int(x.split('-')[1]) for x in filter(lambda k: data[k] == "on", data)]
		start = min(blocks)
		end = max(blocks) + 1
		targetday = int(list(data)[0].split('-')[0])
		today = datetime.date.today()
		twdy = today.weekday()
		starttime = datetime.time.fromisoformat(USE_TIME_STRINGS[start])
		endtime = datetime.time.fromisoformat(USE_TIME_STRINGS[end])
		usedate = today + datetime.timedelta(days=targetday - twdy if twdy <= targetday else 7 - (twdy - targetday))
		database.insertuse(bldginfo[building], bldginfo[building].rooms[room], common.Use(1, usedate, usedate, [common.Time(starttime, endtime, '날')]), stnum, name)
		return flask.render_template("fill.html", name=name)
	else:
		return flask.render_template("fill.html", error=error) #, 422

# 수업있을때, 지난 시간일때, 주말일때, 집채/방 없을때도 잘못 돌려줘야함
def checkerrors(stnum, checkdict):
	if not stnum.isdigit():
		return f"학번 '{stnum}'이 수가 아닙니다."
	checked = list(filter(lambda k: checkdict[k] == "on", checkdict))
	if len(checked) <= 0:
		return "시간을 고르세요."
	# 글일때 늘어놓으면 10, 1이 제대로 안놓임
	checked = sorted([(int(x), int(y)) for x, y in map(lambda z: z.split('-'), checked)], key=lambda x: x[1])
	weekday, last = checked[0]
	for c in checked[1:]:
		w, t = c[0], c[1]
		if w != weekday:
			return "하루 안에서 고르세요."
		if last + 1 != t:
			return "이어진 시간을 고르세요."
		last = t
	return None

@functools.lru_cache(maxsize=None)
def calchue(p):
	return (1 - min(p / ROOM_COLOR_CAP, 1) ** (1 / 3)) * 120
