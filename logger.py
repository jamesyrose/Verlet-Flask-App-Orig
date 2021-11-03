import os
import pandas as pd 
from datetime import datetime
import datetime as dt
import time
import math
import random 
import string


rpath = os.path.dirname(os.path.abspath(__file__))

def date_check(d): 
    """
    Check to make sure the date is correctly formated
    """
    try: 
        nd = int(datetime.strptime(d, "%Y-%m-%d").strftime("%s"))
        twok = 915155786 
        tom = time.mktime(time.localtime(time.time() + 365*24*3600))
        if twok < nd < tom: 
            return True
        else: 
            return False
    except Exception: 
        return False


def find_price(x, res, promo):
    if promo in open(os.path.join(rpath, "files", 'promo_codes.csv')).read() and promo != "" and promo != " ":
        codes = pd.read_csv(os.path.join(rpath, "files", "promo_codes.csv"))
        code = codes[codes["code"] == promo].index[0]
        promo_rate = codes.loc[code, "discount"]
        promo_str = "% + {}".format(promo_rate * 100)
    else:
        promo_rate= 0
        promo_str = ""
    if res.lower() == "minute": 
        base_price = 1.00
    elif res.lower() == "second":
        base_price = 3.00
    # discount factor
    discount = 0.3 * (2**((-x)/27)) + 0.7 - promo_rate
    # price
    price = discount * base_price * x
    if  price < 1:  
        price = 1.00
    return math.floor(price *100) / 100, "{}{}".format(math.floor((100 - discount * 100) *100) /100, promo_str)



def symbol_check(symbols, res, sdate, edate, promo): 
    """
    Check what time range is actually avaliable
    """
    sdate = int(datetime.strptime(sdate, "%Y-%m-%d").strftime("%s"))
    edate = int(datetime.strptime(edate, "%Y-%m-%d").strftime("%s"))
    # getting the dates avaliable 
    if res.lower() == "minute": 
        df = pd.read_csv(os.path.join(rpath, 'files', "minuteava.csv"))
    elif res.lower() == "second": 
        df = pd.read_csv(os.path.join(rpath, "files", "secondava.csv"))
    else: 
        print("Error with resolution")
    df.set_index("Ticker", inplace=True)
    symbol = list(dict.fromkeys(symbols.replace(" ", "").split(",")))
    string = ""
    back_string = ""
    not_found = ""
    day_count = 0
    for s in symbol: 
        try:
            # finding the date range avliabble
            s = s.strip().replace("/", "-")
            rs = int(datetime.strptime(df.loc[s, "Start"], "%Y-%m-%d").strftime("%s"))
            re = int(datetime.strptime(df.loc[s, "End"], "%Y-%m-%d").strftime("%s"))
            if re < sdate  or rs > edate: 
                not_found = "{}{}; ".format(not_found, s )
            else: 
                true_start = sdate if sdate > rs else rs
                true_end = edate if edate < re else re
                # building response string
                string = "{}{}:  &nbsp;&nbsp{} &nbsp;&nbsp  {}<br>".format(string, 
                                                                           s, 
                                                                           datetime.fromtimestamp(true_start).strftime('%Y-%m-%d'),
                                                                           datetime.fromtimestamp(true_end).strftime('%Y-%m-%d'))   
                back_string = "{}--{}-{}-{}".format(back_string, s.replace("-", "/"), true_start, true_end)
                # counting the amount of data for pricing
    
                add_day = math.floor((true_end - true_start) / 86400)
                day_count += add_day
        except Exception as e: 
            print(e)
            not_found = "{}{}; ".format(not_found, s )
    # checking if avaliable tickers is a lot and puts it in a scroll box if nessary 
    if len(string.split("<br>")) > 4: 
        string = """<div style="background:rgba(0, 0, 0, 0.5); 
                    height:125px;width:400px;border:1px solid #ccc; 
                    overflow:auto;">
                    {}
                    </div>""".format(string)
    if len(not_found) > 3:
        if len(not_found) > 52: 
            not_found = """<div style="background:rgba(0, 0, 0, 0.5); 
                            height:35px;width:400px;border:1px solid #ccc; 
                            overflow:auto;">
                            {}
                            </div>""".format(not_found)
        string = "Avaliable Requested Data <hr width='50%' align='left'> {}<br> Data not found for Symbols: <hr width='50%' align='left'> {}".format(string, not_found)
    else: 
        string = "Avaliable Requested Data <hr width='50%' align='left'> {}".format(string)
    # finding number of years 
    years =  math.floor(day_count / 365 * 1000) /1000
    price, discount = find_price(years, res, promo)
    string = "<h4><font color=white size='-.5'> {} <br>Number of Years of Data: <hr width='50%' align='left'> {} years <br><br> Price: <hr width='50%' align='left'> $ {} ({}% discount)</font></h4>".format(string, years, price, discount)
    return string, price, back_string

def id_generator(size=24, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def send_req(un_id, email, data, price, token, order_time):
    log_path = os.path.join(rpath, "request_log.csv")
    if un_id not in os.popen("grep {} {}".format(un_id, 
                                                 log_path)).read(): 
        os.system("echo 'No,{},{},{},{},{},NotUploaded,{}' >> {}".format(un_id, 
                                                             email.replace("AT", "@"),
                                                             data, 
                                                             price, 
                                                             token,
                                                             order_time,
                                                             log_path))


def gen_data(un_id, email, data, price, token, order_time):
    log_path = os.path.join(rpath, "request_log.csv")
    if un_id not in os.popen("grep {} {}".format(un_id, 
                                                 log_path)).read(): 
        req_string = 'No,{},{},{},{},{},{}'.format(un_id, 
                                                   email.replace("AT", "@"),
                                                   data, 
                                                   price, 
                                                   token,
                                                   order_time
                                                   ).replace("\n", "")
        os.system("echo '{}' >> {}".format(req_string,
                                           log_path)
                                           )
    while "No" in os.popen("grep '{}' {} | cut -c 1-3".format(un_id, 
                                                              log_path)).read(): 
        time.sleep(5) 

def check_download_exists(un_id, email):
   log_path = os.path.join(rpath, "request_log.csv")
   if "UPLOADED" in os.popen("grep '{}' {} | grep '{}'".format(un_id, log_path, email)).read():
       return True
   else: 
       return False

def reorder(un_id, email):
   log_path = os.path.join(rpath, "request_log.csv")
   req = os.popen("grep '{}' {} | grep '{}' ".format(un_id, log_path, email)).read()
   command = "sed -i 's/{}/{}/g' " \
             "/home/verletio/web_main/request_log.csv; "\
             "echo '{}' >> /home/verletio/web_main/request_log.csv".format(req.replace("\n", ""),
                                                                           un_id,
                                                                           req.replace("\n", "")
                                                                              .replace("Yes,", "No,").replace("UPLOADED", "NotUploaded"))
   os.system(command)
    
if __name__ =="__main__": 
    symbol_check("JNUG,AAPL", "minute","2013-11-01", "2019-11-01")
