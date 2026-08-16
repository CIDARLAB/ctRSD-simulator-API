# ctRSD-Simulator-API
Based on https://github.com/usnistgov/ctRSD-simulator

## Docs
https://ctrsd-simulator.readthedocs.io/en/latest/

## Quickstart

### Docker Instructions
1) Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2) Clone this repository
3) run `docker build -t seq-compiler .` in the root of this repo
4) run `docker run -p 8010:8010 seq-compiler`
5) Open FastAPI Docs at http://localhost:8010/docs

### Non-Docker Instructions
1) Clone this repository
2) Install dependencies `pip install -r requirements.txt` or import `environment.yml` to conda
3) Run `uvicorn app.main:api --reload --host 127.0.0.1 --port 8010` in the root directory of this repo
4) Open FastAPI Docs at http://localhost:8010/docs
