import flask
import json

import processraw

with open("raw/lectures.json") as f:
	bldginfo = processraw.process(json.load(f))

app = flask.Flask(__name__)

@app.route("/")
def root():
	return flask.render_template("root.html", buildings=sorted(list(bldginfo)))

@app.route("/rooms/<building>")
def rooms(building):
	try:
		bldg = bldginfo[building]
	except KeyError:
		return "건물이 없습니다"
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
	return flask.render_template("use.html", building=building, room=room, timeblocks=["09:00~09:30", "09:00~09:30", "09:00~09:30", "09:00~09:30"])
