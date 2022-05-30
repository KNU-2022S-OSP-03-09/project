import json
import re

from common import *

def _split_building(buildingname):
	"""여러 집채에 걸친 강의가 있어서 만듦."""
	ends = ["관", "센타"]
	for end in ends:
		index = buildingname.find(end)
		if index >= 0 and index != len(buildingname) - len(end):
			return buildingname[:index + len(end)], buildingname[index + len(end):]
	return [buildingname]

def _split_room(roomname):
	# '601B'가 있어서
	if roomname[-1] == 'B' and len(roomname) <= 4:
		return [roomname]
	count = 0
	explen = 3
	splits = [0]
	for i, c in enumerate(roomname):
		# 안가지/뒷가지
		if c == '-':
			# 'B01-2' 같은 이름이 있어서
			if explen >= 4:
				explen += 1
			else:
				explen += 2
		elif c == 'A':
			explen += 1
		elif count == explen:
			count = 0
			explen = 3
			splits.append(i)
		# 앞가지
		if c == 'B' or c == 'S':
			explen += 1
		count += 1
	splits.append(len(roomname))
	return [roomname[splits[i]:splits[i + 1]] for i in range(len(splits) - 1)]

def process(data):
	"""
	crawl에서 얻은 데이터를 갈망함.
	:param data: [dict]
	lctrmInfo 강의실
	rmnmCd 호실번호
	lssnsTimeInfo 강의시간
	lssnsRealTimeInfo 강의시간(실제시간)
	rmrk 비고(상주캠퍼스, 원격수업)
	sbjetNm 교과목명
	crseNo 강좌번호"""
	buildings = dict()
	for l in data:
		remark = l["rmrk"]
		if remark is not None and ("원격" in remark or "상주캠퍼스" in remark):
			continue

		bldg = l["lctrmInfo"]
		# 의생명과학관: 팔거리 친환경농업교육및연구센터: 노동멱고장 복지후생동: 새위마을
		if bldg is None or any(ss in bldg for ss in ["운동장", "수영장", "테니스장", "체육관", "대강당", "학군단", "병원", "치대", "의대", "의생명과학관", "친환경농업교육및연구센터", "복지후생동"]):
			continue
		if re.fullmatch("제[0-9]+호관", bldg) is not None:
			continue
		bldg = re.sub(r"\(.*\)", "", bldg)
		bldg = _split_building(bldg)
		for b in bldg:
			if b not in buildings:
				buildings[b] = Building(b)

		#use = Use(99999, ?, ?, times, l["crseNo"])

		room = _split_room(l["rmnmCd"])
		if len(bldg) >= 2:
			for i, b in enumerate(bldg):
				buildings[b].rooms[room[i]] = Room(room[i])
		else:
			for r in room:
				buildings[bldg[0]].rooms[r] = Room(r)
	return buildings
