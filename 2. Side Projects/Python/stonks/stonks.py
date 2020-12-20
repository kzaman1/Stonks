import pandas as pd
from pandas import ExcelWriter
from alpha_vantage.timeseries import TimeSeries
import time
from credentials import *
import matplotlib.pyplot as plt

ts = TimeSeries(key=api_key, output_format='pandas')

a = 0
call_limit = [4, 8, 12]

writer = ExcelWriter('output.xlsx')

for i in stock_list:
    stonk_data, meta_data = ts.get_monthly(symbol=i)
    index=stonk_data.index
    index.name= "Stock: " + i
    close_data = stonk_data['4. close']
    percentage_change = close_data.pct_change() * 100
    stonks = "STOCK:", i, close_data, percentage_change
    print(stonk_data['4. close'])
    a += 1
    print("a =", a)
    file_name = i + " - Sheet - " + str(a)
    print(file_name)
    #Matplotlib will print a plot of each stock, how do i print them all in one view?
    #df = pd.DataFrame(stonk_data, columns=['4. close'])
    #df.plot(kind = 'line')
    #plt.show()
    stonk_data['4. close'].to_excel(writer, sheet_name=file_name)
    if a in call_limit:
        print("Sleep . . . 45 seconds")
        time.sleep(45)

writer.save()
