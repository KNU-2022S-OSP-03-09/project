# 어디비나

어느 강의실이 비었는지 보여주는 누리집

## 돌리기

### 1. 내려받고 setup 돌리기

```
git clone https://github.com/KNU-2022S-OSP-03-09/project.git
cd project
./setup
```

### 2. 긁을(crawling) 준비

**데이터를 스스로 긁으려면** tools 폴더에 [geckodriver](https://github.com/mozilla/geckodriver/releases/), tools/firefox 폴더에 [firefox](https://www.mozilla.org/ko/firefox/linux/)를 넣는다.

파이어폭스는 통째로 tools에 압축풀어도 되고, 시스템에 깔려 있으면

```
mkdir tools/firefox
ln -s /usr/bin/firefox tools/firefox/firefox
```

해도 된다.

**이미 있는 데이터를 쓰려면** raw 폴더에 lectures.json을 넣는다.

셋 다 넣었을 때의 폴더 얼개는 아래와 같다.

```
.
|-- raw
|   `-- lectures.json
`-- tools
    |-- geckodriver
    `-- firefox
        |-- firefox
        `-- (파이어폭스를 통째로 압축풀었다면) 파이어폭스 파일들..
```

### 3. 데이터베이스 고르고 누리집 켜기

#### SQLite

```
./run
```

#### PostgreSQL

**! 우분투/데비안에서는 setuppostgres가 안 돌아가니 SQLite를 쓰기 바람 !**

PostgreSQL을 시스템에 깔고

```
./setuppostgres
./runwithpg
```

## 그물(네트워크)에 열기

`run`의 마지막 줄을 바꾸면 된다.

`$PYTHON_COMMAND -m flask run --host 0.0.0.0`

`$PYTHON_COMMAND -m gunicorn -b 0.0.0.0 app:app`

들들

## 걸림풀이(troubleshooting)

`./setup`에서

```
It appears you are missing some prerequisite to build the package from source.

You may install a binary package by installing 'psycopg2-binary' from PyPI.
If you want to install psycopg2 from source, please install the packages
required for the build and try again.
```

라고 뜨면

- libpq를 깔거나(우분투: `sudo apt install libpq-dev`)
- requirements.txt에서 `psycopg2` 줄을 지우고 PostgreSQL을 쓰지 않으면 된다.

## 폴더 풀이

- db: 데이터베이스
- raw: lecture.json
- tools: geckodriver, firefox/firefox
- venv: 가상 환경
