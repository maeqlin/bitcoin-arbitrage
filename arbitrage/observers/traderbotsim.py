import logging
from .traderbot import TraderBot
import json


class MockMarket(object):
    def __init__(self, name, fee=0, usd_balance=500., btc_balance=15.,
                 persistent=True):
        self.name = name
        self.filename = "traderbot-sim-" + name + ".json"
        self.usd_balance = usd_balance
        self.btc_balance = btc_balance
        self.fee = fee
        self.persistent = persistent
        if self.persistent:
            try:
                self.load()
            except IOError:
                pass

    def buy(self, volume, price):
        logging.info("execute buy %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.usd_balance -= price * volume
        self.btc_balance += volume - volume * self.fee
        if self.persistent:
            self.save()

    def sell(self, volume, price):
        logging.info("execute sell %f BTC @ %f on %s" %
                     (volume, price, self.name))
        self.btc_balance -= volume
        self.usd_balance += price * volume - price * volume * self.fee
        if self.persistent:
            self.save()

    def load(self):
        data = json.load(open(self.filename, "r"))
        self.usd_balance = data["usd"]
        self.btc_balance = data["btc"]

    def save(self):
        data = {'usd': self.usd_balance, 'btc': self.btc_balance}
        json.dump(data, open(self.filename, "w"))

    def balance_total(self, price):
        return self.usd_balance + self.btc_balance * price

    def get_info(self):
        pass


class TraderBotSim(TraderBot):
    def __init__(self):
        self.kraken = MockMarket("kraken", 0.005, 5000) # 0.5% fee
        self.paymium = MockMarket("paymium", 0.005, 5000) # 0.5% fee
        self.bitstamp = MockMarket("bitstamp", 0.005, 5000) # 0.5% fee
        self.btcc = MockMarket("btcc", 0.005, 5000) # 0.5% fee
        self.clients = {
            "KrakenEUR": self.kraken,
            "PaymiumEUR": self.paymium,
            "BitstampUSD": self.bitstamp,
            "BTCCCNY": self.btcc,
        }
        self.profit_thresh = 10  # in EUR
        self.perc_thresh = 0.02  # in %
        self.trade_wait = 120
        self.last_trade = 0

    def total_balance(self, price):
        market_balances = [i.balance_total(
            price) for i in set(self.clients.values())]
        return sum(market_balances)

    def total_usd_balance(self):
        return sum([i.usd_balance for i in set(self.clients.values())])

    def total_btc_balance(self):
        return sum([i.btc_balance for i in set(self.clients.values())])

    def execute_trade(self, volume, kask, kbid,
                      weighted_buyprice, weighted_sellprice,
                      buyprice, sellprice):
        self.clients[kask].buy(volume, buyprice)
        self.clients[kbid].sell(volume, sellprice)

if __name__ == "__main__":
    t = TraderBotSim()
    print("Total BTC: %f" % t.total_btc_balance())
    print("Total USD: %f" % t.total_usd_balance())
