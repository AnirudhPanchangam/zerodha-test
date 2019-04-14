import os
import requests
from datetime import datetime, timedelta
import zipfile
import csv
import json
import redis
import logging


BASE_URL = "https://www.bseindia.com/download/BhavCopy/Equity/EQ%s_CSV.ZIP"

logger = logging.getLogger(__name__)

class PreProcess(object):
    
    def make_url(self):
        try:
            curr_time = datetime.now() - timedelta(1)
            day = str(curr_time.day)
            month = str(curr_time.month)
            year = str(curr_time.year % 100)
            if len(day) == 1:
                day = "0" + day
            if len(month) == 1:
                month = "0"+month
            url = BASE_URL%(day + month + year)
            return url
        except Exception as e:
            logger.error(e)
            
    def download_file(self, url):
        try:
            local_filename = url.split('/')[-1]
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): 
                        if chunk:
                            f.write(chunk)
            return local_filename
        except Exception as e:
            logger.error(e)

    def unzip_file(self, filename):
        try:
            zip_ref = zipfile.ZipFile(filename, 'r')
            zip_ref.extractall("./equity/")
            zip_ref.close()
            os.remove(filename)
            return "./equity/" + filename.split('_')[-2] + ".CSV"
        except Exception as e:
            logger.error(e)


    def update_redis(self, filename):
        try:
            conn = redis.Redis()
            key = "stock_codes"
            with open(filename) as f:
                csv_reader = csv.reader(f, delimiter=',')
                for i, row in enumerate(csv_reader):
                    if i ==0:
                        continue
                    d = {}
                    li = row[:]
                    del li[8:]
                    del li[1:4]
                    print(li)
                    li = json.dumps(li)
                    #SC_GROUP,SC_TYPE,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,NO_TRADES,NO_OF_SHRS,NET_TURNOV,TDCLOINDI,SC_CODE
                    d[row[1].rstrip()] = li
                    conn.hmset(key, d)
        except Exception as e:
            logger.error(e)
    def run(self):
        try:
            url = self.make_url()
            print("Url Obtained")    
            filename = self.download_file(url)
            print("file downloaded")
            filename = self.unzip_file(filename)
            print("File unzipped")
            self.update_redis(filename)
        except Exception as e:
            logger.error(e)
if __name__ == '__main__':
    pp = PreProcess()
    url = pp.make_url()    
    filename = pp.download_file(url)
    filename = pp.unzip_file(filename)
    pp.update_redis(filename)





    