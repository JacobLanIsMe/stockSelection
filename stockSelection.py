import requests, time, pandas, bs4, json
starttime = time.time()
def linenotifymessage(token, msg):
    headers = {"Authorization": "Bearer "+token,"Content-Type":"application/x-www-form-urlencoded"}
    message = {"message":msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = message)
    return r.status_code
print("代碼","名稱","類股","現價","法人買超天數","法人買超張數","投信買超天數","投信買超張數", "月營收月增(%)","月營收年增(%)","累計月營收年增(%)","月營收連續N個月遞增")
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"}
stock_name = pandas.read_csv("name.csv")
stock = [str(i) for i in stock_name["代碼"].to_list()]
#classification = stock_name["產業類別"].to_list()
#conception = stock_name["概念股"].to_list()
v10, backbuy, advantage = [], [], []
for d in stock:
    try:
        url_name = "https://tw.quote.finance.yahoo.net/quote/q?type=ta&perd=d&mkt=10&sym="+d+"&v=1&callback=jQuery111306311117094962886_1574862886629&_=1574862886630"
        web_name = requests.get(url_name).text.replace("jQuery111306311117094962886_1574862886629(","").rstrip(");")
        info = json.loads(web_name)
        name = info["mem"]["name"]
        data = info["ta"]
        day, open_, high, low, close, vol = [], [], [], [], [], []
        for i in data:
            day.append(str(i["t"]))
            open_.append(i["o"])
            high.append(i["h"])
            low.append(i["l"])
            close.append(i["c"])
            vol.append(i["v"])
        day, open_, high, low, close, vol = day[::-1], open_[::-1], high[::-1], low[::-1], close[::-1], vol[::-1]
        lastmonth = close[:40]
        maxclose = max(lastmonth)
        maxcloseindex = lastmonth.index(maxclose)
        tMA5 = sum(close[:5])/5
        tMA20 = sum(close[:20])/20
        tMV5 = sum(vol[:5])/5
        if (maxclose>=max(close[maxcloseindex+1:maxcloseindex+21]) and maxcloseindex>=1 and vol[0]>=500 and close[0]>=tMA5 and
        min(close[:maxcloseindex+1])>=min(close[maxcloseindex+1:maxcloseindex+21])):
            c1, c2, c3, c4 = 0, 0, 0, 0
            for i in range(1,4):
                if close[0]>high[i]:
                    c1+=1
            for i in range(2,5):
                if close[1]>high[i]:
                    c2+=1
            for i in range(3,6):
                if close[2]>high[i]:
                    c3+=1
            for i in range(4,7):
                if close[3]>high[i]:
                    c4+=1
            if (c1>=2 and c2<2 and c3<2) or (close[0]>close[1] and c2>=2 and c3<2 and c4<2):
                url_three = "https://histock.tw/stock/chips.aspx?no="+d
                web_three = requests.get(url_three).text
                soup_three = bs4.BeautifulSoup(web_three, "html.parser")
                style = soup_three.select("span#Price1_lbStockClass2")[0].text
                three = [i.text for i in soup_three.select("tr td")]
                #foreign = [int(i.replace(",","")) for i in three[1::6]]
                trust = [int(i.replace(",","")) for i in three[2::6]]
                #self1 = [int(i.replace(",","")) for i in three[3::6]]
                #self2 = [int(i.replace(",","")) for i in three[4::6]]
                #self = [self1[i]+self2[i] for i in range(len(self1))]
                three_sum = [int(i.replace(",","")) for i in three[5::6]]
                three_buy_day = 0
                for i in three_sum[:maxcloseindex]:
                    if i > 0:
                        three_buy_day += 1
                three_buy_day = str(three_buy_day)+"/"+str(maxcloseindex)
                trust_buy_day = 0
                for i in trust[:maxcloseindex]:
                    if i > 0:
                        trust_buy_day += 1
                trust_buy_day = str(trust_buy_day)+"/"+str(maxcloseindex)
                url_revenue = "https://histock.tw/stock/"+d+"/%E8%B2%A1%E5%8B%99%E5%A0%B1%E8%A1%A8"
                web_revenue = requests.get(url_revenue).text
                soup_revenue = bs4.BeautifulSoup(web_revenue, "html.parser")
                revenue = soup_revenue.select("tr td")
                revenue_m = [int(i.text.replace(",","")) for i in revenue[1::8]]
                revenue_MOM = float(revenue[3].text.rstrip("%"))
                revenue_YOY = float(revenue[4].text.rstrip("%"))
                revenue_plusYOY = float(revenue[7].text.rstrip("%"))
                revenue_increase_count = 0
                for i in range(len(revenue_m)):
                    if revenue_m[i]>revenue_m[i+1]:
                        revenue_increase_count += 1
                    else:
                        break
                
                if low[0]>=high[1]:
                    print("#"+d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count)
                    v10.append(["#"+d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count])
                else:
                    print(d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count)
                    v10.append([d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count])        
        if (maxclose>=max(close[maxcloseindex+1:maxcloseindex+21]) and maxcloseindex>=3 and vol[0]>=500 and close[0]>=tMA20 and
            min(close[:maxcloseindex+1])>=min(close[maxcloseindex+1:maxcloseindex+21])):
            count_MA10 = 0
            count_MA20 = 0
            for i in range(8):
                if close[i]>=sum(close[i:i+10])/10:
                    count_MA10 += 1
            for i in range(10):
                if close[i]>=sum(close[i:i+20])/20:
                    count_MA20 += 1
            if (count_MA10>=7 and max(close[:5])/min(close[:5])<=1.06) or (count_MA20>=7 and max(close[:5])/min(close[:5])<=1.1):
                url_three = "https://histock.tw/stock/chips.aspx?no="+d
                web_three = requests.get(url_three).text
                soup_three = bs4.BeautifulSoup(web_three, "html.parser")
                style = soup_three.select("span#Price1_lbStockClass2")[0].text
                three = [i.text for i in soup_three.select("tr td")]
                #foreign = [int(i.replace(",","")) for i in three[1::6]]
                trust = [int(i.replace(",","")) for i in three[2::6]]
                #self1 = [int(i.replace(",","")) for i in three[3::6]]
                #self2 = [int(i.replace(",","")) for i in three[4::6]]
                #self = [self1[i]+self2[i] for i in range(len(self1))]
                three_sum = [int(i.replace(",","")) for i in three[5::6]]
                three_buy_day = 0
                for i in three_sum[:maxcloseindex]:
                    if i > 0:
                        three_buy_day += 1
                three_buy_day = str(three_buy_day)+"/"+str(maxcloseindex)
                trust_buy_day = 0
                for i in trust[:maxcloseindex]:
                    if i > 0:
                        trust_buy_day += 1
                trust_buy_day = str(trust_buy_day)+"/"+str(maxcloseindex)
                url_revenue = "https://histock.tw/stock/"+d+"/%E8%B2%A1%E5%8B%99%E5%A0%B1%E8%A1%A8"
                web_revenue = requests.get(url_revenue).text
                soup_revenue = bs4.BeautifulSoup(web_revenue, "html.parser")
                revenue = soup_revenue.select("tr td")
                revenue_m = [int(i.text.replace(",","")) for i in revenue[1::8]]
                revenue_MOM = float(revenue[3].text.rstrip("%"))
                revenue_YOY = float(revenue[4].text.rstrip("%"))
                revenue_plusYOY = float(revenue[7].text.rstrip("%"))
                revenue_increase_count = 0
                for i in range(len(revenue_m)):
                    if revenue_m[i]>revenue_m[i+1]:
                        revenue_increase_count += 1
                    else:
                        break
                print(d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count)
                backbuy.append([d, name, style, close[0], three_buy_day, sum(three_sum[:maxcloseindex]), trust_buy_day, sum(trust[:maxcloseindex]), revenue_MOM, revenue_YOY, revenue_plusYOY, revenue_increase_count])
        advantage_count = 0
        for i in range(5):
            if close[i]>=sum(close[i:i+5])/5:
                if close[i]>=sum(close[i:i+20])/20 or close[i]>=sum(close[i:i+60])/60:
                    advantage_count += 1
        if advantage_count == 5 and max(close[:5])/min(close[:5]) <= 1.03 and vol[0] >= 500:
            print(d, name, close[0])
            advantage.append([d, name, close[0]])
    except:
        continue
df_v10 = pandas.DataFrame(v10, columns=["代碼","名稱","類股","現價","法人買超天數","法人買超張數", "投信買超天數", "投信買超張數", "月營收月增(%)","月營收年增(%)","累計月營收年增(%)","月營收連續N個月遞增"])
df_v10.to_csv("v10_"+ time.strftime("%Y%m%d", time.localtime(time.time())) + ".csv", encoding = "utf_8_sig", index = False)
df_backbuy = pandas.DataFrame(backbuy, columns=["代碼","名稱","類股","現價","法人買超天數","法人買超張數", "投信買超天數", "投信買超張數", "月營收月增(%)","月營收年增(%)","累計月營收年增(%)","月營收連續N個月遞增"])
df_backbuy.to_csv("backbuy_"+ time.strftime("%Y%m%d", time.localtime(time.time())) + ".csv", encoding = "utf_8_sig", index = False)
df_advantage = pandas.DataFrame(advantage, columns=["代碼","名稱", "收盤價"])
df_advantage.to_csv("advantage_"+ time.strftime("%Y%m%d", time.localtime(time.time())) + ".csv", encoding = "utf_8_sig", index = False)
v10s, backbuys, advantages = ["回後買上漲:"], ["慣性改變:"], ["維持在五日線上:"]
v10d = [str(i) for i in df_v10["代碼"].to_list()]
v10name = df_v10["名稱"].to_list()
for i in range(len(v10d)):
    v10s.append(v10d[i]+v10name[i])
backbuyd = [str(i) for i in df_backbuy["代碼"].to_list()]
backbuyname = df_backbuy["名稱"].to_list()
for i in range(len(backbuyd)):
    backbuys.append(backbuyd[i]+backbuyname[i])
advantaged = [str(i) for i in df_advantage["代碼"].to_list()]
advantagename = df_advantage["名稱"].to_list()
for i in range(len(advantaged)):
    advantages.append(advantaged[i]+advantagename[i])
v10s = ",".join(v10s)
backbuys = ",".join(backbuys)
advantages = ",".join(advantages)
token = "rTL9NaAgcNZv3TH0YU9OSwk0N3Crl2hRO7ZStqCGLi5"
msg1 = v10s
msg2 = backbuys+";"+advantages
linenotifymessage(token, msg1)
linenotifymessage(token, msg2)
endtime = time.time()
print("總共執行:", " ", str(endtime-starttime), "秒")
