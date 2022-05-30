import flask

app = flask.Flask(__name__)

@app.route("/")
def root():
	return flask.render_template("root.html", buildings=["IT대학 11호관", "공과대학 22호관"])

@app.route("/rooms/<building>")
def rooms(building):
	return flask.render_template("rooms.html", building=building, rooms=["101", "201", "301"])

@app.route("/use/<building>/<room>")
def use(building, room):
	return flask.render_template("use.html", building=building, room=room, timeblocks=["09:00~09:30", "09:00~09:30", "09:00~09:30", "09:00~09:30"])
