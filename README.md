# Python RSI-Notifications-Bot

## Description
This bot sends RSI signals in telegram using the BINANCE platform and the TA-Lib library.

## Technology Stack

- Python
- SQLAlchemy
- AioSQLite
- TA-Lib
- Aiogram
- Aiohttp

## Installation

### First you need to install the TA-Lib library

- Windows

You need to download the file **TA_Lib-0.4.28-cp311-cp311-win_amd64.whl** and place it in this path C:\Users\admin\

> If your path is different from mine, then fix it in the poetry.lock and pyproject.toml files

```
pip install A_Lib-0.4.28-cp311-cp311-win_amd64.whl
```

- Linux

> Before working, remove the TA-Lib dependency from the poetry.lock and pyproject.toml files

```
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xvzf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

### Installing other dependencies:
```
pip install poetry
poetry env use python
poetry shell
poetry install
```

## Running

```
poetry run python main.py
```