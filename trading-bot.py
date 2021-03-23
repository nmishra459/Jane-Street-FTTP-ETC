#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# 1) Configure things in CONFIGURATION section
# 2) Change permissions: chmod +x bot.py
# 3) Run in loop: while true; do ./bot.py; sleep 1; done

from __future__ import print_function

import sys
import socket
import json

# ~~~~~============== CONFIGURATION  ==============~~~~~
# team name
team_name="psyduck"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = True

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

num_order = 0

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def bondProcesses(exchange):
    global num_order

    num_order+=1
    write_to_exchange(exchange, {"type": "add", "order_id": order_no, "symbol": "BOND", "dir": "SELL", "price": 1002, "size": 10})

    num_order+=1
    write_to_exchange(exchange, {"type": "add", "order_id": order_no, "symbol": "BOND", "dir": "BUY", "price": 998, "size": 10})

# ~~~~~============== MAIN LOOP ==============~~~~~
def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while True:
        message = read_from_exchange(exchange)
        if (message["type"] == "close"):
            print("The round has ended")
            break
        elif (message["type"] == "book"):
            symbol = message["symbol"]
            print(symbol)

            buy = message["buy"]
            sell = message["sell"]
            if (len(buy) == 0 or len(sell) == 0):
                continue

            bid_price = buy[0][0]
            bid_volume = buy[0][1]
            ask_price = sell[0][0]
            ask_volume = sell[0][1]
            fair_price = (bid_price + ask_price) / 2

            if (ask_price - bid_price >= 4):
                write_to_exchange(exchange, {"type": "add", "order_id": num_order, "symbol": symbol, "dir": "BUY", "price": (bid_price + 1), "size": 10})
                write_to_exchange(exchange, {"type": "add", "order_id": num_order, "symbol": symbol, "dir": "SELL", "price": (ask_price - 1), "size": 10})

if __name__ == "__main__":
    main()
