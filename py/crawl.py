import json
import os
import pathlib
import random
import time

from seleniumwire import webdriver
from seleniumwire import utils
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

def _sweep(depth, selects, searchbutton, driver):
	result = []
	startindex = 1 if selects[depth][0].options[0].text == "선택" else 0
	for i in range(startindex, len(selects[depth][0].options)):
		time.sleep(random.random() + 0.7)
		selects[depth][0].select_by_index(i)
		try:
			driver.wait_for_request("/public/web/stddm/lsspr/syllabus/lectPlnInqr/selectItttnCdListLectPlnInqr", timeout=3)
			del driver.requests
		except TimeoutException:
			pass
		if depth + 1 < len(selects) and selects[depth + 1][1].is_displayed():
			result += _sweep(depth + 1, selects, searchbutton, driver)
		else:
			time.sleep(random.random() / 2 + 0.2)
			searchbutton.click()
			resp = driver.wait_for_request("/public/web/stddm/lsspr/syllabus/lectPlnInqr/selectListLectPlnInqr").response
			result += json.loads(utils.decode(resp.body, resp.headers.get("Content-Encoding", "identity")))["data"]
			del driver.requests
	return result

def crawl():
	options = Options()
	options.headless = True
	service = Service(executable_path="tools/geckodriver")
	with webdriver.Firefox(firefox_binary="tools/firefox/firefox", options=options, service=service) as driver:
		driver.scopes = [
			"/public/web/stddm/lsspr/syllabus/lectPlnInqr/selectItttnCdListLectPlnInqr",
			"/public/web/stddm/lsspr/syllabus/lectPlnInqr/selectListLectPlnInqr"
		]

		driver.get("https://knuin.knu.ac.kr/public/stddm/lectPlnInqr.knu")
		try:
			WebDriverWait(driver, 20).until(presence_of_element_located((By.ID, "schSbjetCd1")))
		except TimeoutException:
			return None
		# presence_of_element_located 뒤에도 select에 option이 채워지지 않을 때가 있음. expected_condition 하나 만들어서 기다리면 좋겠지만 time.sleep도 먹힘
		time.sleep(2)
		selects = []
		for i in range(1, 5):
			# Select._el은 안읽는게 좋을듯
			element = driver.find_element(By.ID, f"schSbjetCd{i}")
			selects.append((Select(element), element))
		searchbutton = driver.find_element(By.ID, "btnSearch")

		result = _sweep(0, selects, searchbutton, driver)

		return result

def crawl_and_save(path="raw/lectures.json"):
	crawled = crawl()
	pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		json.dump(crawled, f, ensure_ascii=False)
	return crawled
