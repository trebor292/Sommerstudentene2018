import urllib.request
import datetime
import time
import requests
import BaneSegment

current_forecast = None 
http = "http://thredds.met.no/thredds/catalog/meps25files/catalog.html?dataset=meps25files/meps_det_pp_2_5km_latest.nc"
url = "http://thredds.met.no/thredds/fileServer/meps25files/meps_det_pp_2_5km_latest.nc"
f_name = "c:/Users/student/Desktop/netCDF/met_forecast/meps_det_pp_2_5km_latest.nc"

while True:
    now = datetime.datetime.now()
    fp = urllib.request.urlopen(http)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    t = mystr.split(str(now.year))
    new_forecast = str(now.year) + t[1][0:9]
    
    #if new_forecast != current_forecast:
     #   print("Downloading new forecast")
      #  current_forecast = new_forecast
       # urllib.request.urlretrieve(url,f_name)
        #print("Forecast downloaded")
        #print("Starting joachim script")
        #BaneSegment.joachim_script()
    BaneSegment.joachim_script()
    print("Sleeping for an hour...")
    #time.sleep(3600)
    break         