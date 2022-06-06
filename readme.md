## 돌리기

```
git clone https://github.com/KNU-2022S-OSP-03-09/project.git
cd project
./setup
```

raw 폴더에 lectures.json 넣거나 tools 폴더에 geckodriver, tools/firefox 폴더에 firefox 넣고

### SQLite

```
./run
```

### PostgreSQL

py/database.py에서 DBMS를 1로 맞추고

```
./setuppostgres
./runwithpg
```


## 폴더 풀이
- db: 데이터베이스
- raw: lecture.json
- tools: geckodriver, firefox/firefox
- venv: 가상 환경
