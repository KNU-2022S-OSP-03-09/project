## 돌리기

```
git clone https://github.com/KNU-2022S-OSP-03-09/project.git
cd project
./setup
```

raw 폴더에 lectures.json 넣거나 tools 폴더에 geckodriver, tools/firefox 폴더에 firefox 넣어 아래처럼 만들고

```
.
|-- raw
|   `-- lectures.json
`-- tools
    |-- geckodriver
    `-- firefox
        |-- firefox
        `-- 파이어폭스 파일들..
```

### SQLite

```
./run
```

### PostgreSQL

```
./setuppostgres
./runwithpg
```


## 폴더 풀이
- db: 데이터베이스
- raw: lecture.json
- tools: geckodriver, firefox/firefox
- venv: 가상 환경
