import yfinance as yf

goog = yf.Ticker("GOOG")

print(goog)

print(goog.info)