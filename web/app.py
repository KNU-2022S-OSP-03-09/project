import datetime
import functools
import json
import math

import apscheduler.schedulers.background
import flask

import common
import database
import processraw

BLOCK_SIZE = 30 * 60
OPEN_SECOND = 9 * 60 * 60
CLOSE_SECOND = 18 * 60 * 60
BLOCK_STRINGS = [f"{(OPEN_SECOND + BLOCK_SIZE * i) // 3600:02}:{(OPEN_SECOND + BLOCK_SIZE * i) % 3600 // 60:02}" for i in range(math.ceil((CLOSE_SECOND - OPEN_SECOND) / BLOCK_SIZE))]
ROOM_COLOR_CAP = 40

with open("raw/lectures.json", encoding="utf-8") as f:
	bldginfo = processraw.process(json.load(f))

app = flask.Flask(__name__)

scheduler = apscheduler.schedulers.background.BackgroundScheduler()
scheduler.start()

@scheduler.scheduled_job(trigger="cron", hour=0, minute=30)
def clearuses():
	database.clearuses(datetime.date.today())

@app.route("/")
def root():
	return flask.render_template("root.html", buildings=sorted(list(bldginfo)))

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

@app.route("/use/<building>/<room>")
def use(building, room):
	try:
		bldg = bldginfo[building]
		rm = bldg.rooms[room]
	except KeyError:
		return flask.render_template("error.html", error=f"'{building} {room}'(이)라는 방이 없습니다")

	useruses = database.queryuses(bldg, rm, datetime.date.today())
	blocks = rm.calcblocks(datetime.date.today(), useruses, BLOCK_SIZE, OPEN_SECOND, CLOSE_SECOND)
	blocks = [(BLOCK_STRINGS[i], "BLOCKED" if b == common.Use.BLOCKING_SIZE else b, calchue(b)) for i, b in enumerate(blocks)]
	return flask.render_template("use.html", building=building, room=room, timeblocks=blocks)

@app.route("/success", methods=["POST"])
def success():
	return flask.render_template("success.html", times=flask.request.form)

@functools.lru_cache(maxsize=None)
def calchue(p):
	return (1 - min(p / ROOM_COLOR_CAP, 1) ** (1 / 3)) * 120
