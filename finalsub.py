
import pandas as pd 
import numpy as np
import bar_chart_race as bcr
import pycountry_convert as pc
import os
import requests
import zipfile

r = requests.Session()
download = "https://storage.googleapis.com/kaggle-data-sets/1093816/2380918/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20210629%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20210629T210811Z&X-Goog-Expires=259199&X-Goog-SignedHeaders=host&X-Goog-Signature=70e3dbd4e2032b11977b568a879bcf5bef47dee245a9a467211bcefacb2d73c1a9c1e5ff9ff0f8dd2b476283e8804dbe727200dbd05975918c7b4326c86e4e109d7f5d0a1dff0fc205a9a98d84310eb840cd938fc7c2a07310b17b1cf95d873152a773ab6ac918ef89f63328c697f19658fe698ab1a464577bfa349ed77f077010851875c3637268f0452dc0a3bf04c02f05337d3176009050ac427db394c767b84fb0fc3305b6d1e1cbe0dab4a3f54634779a18b2e6eefdafb74e46a87822cc6fa9c4cb9bd6973e03015822f50820a7a368ac6de579d012bf1b104da953035ec798bad64892b9be0c90c13d7d2fe2f6f8c459b553bc79b84a34d41a9aef9345"

home = os.path.expanduser("~")
home.replace("\\","/")
home+="/Downloads"
zip1 = home + "/" + "country_vaccinations" + ".zip"

#The image link for each facebook photo can now be downloaded with requests(without login info)
with open(zip1,"wb") as f:
    f.write(r.get(download).content)

with zipfile.ZipFile(zip1,"r") as zip_read:
    zip_read.extractall(home)

destination = home + "/" + "country_vaccinations.csv"


vaccines = pd.read_csv(destination,parse_dates=["date"],dayfirst=True)

vaccines.insert(8, "total_vac", '')
vaccines["total_vac"][0] = vaccines["daily_vaccinations_per_million"][0]
total = 0
current = "Afghanistan"
for i in range(1,len(vaccines["country"])):
    next1 = vaccines["country"][i]
    if current == next1:
        total += vaccines["daily_vaccinations_per_million"][i]
        vaccines["total_vac"][i] = total
    else:
        total = 0
    current = vaccines["country"][i]



from datetime import date, timedelta

sdate = min(vaccines["date"])
edate = max(vaccines["date"])
# sdate = date(2020,12,2)   # start date
# edate = date(2021,6,26) 
Dates = pd.date_range(sdate,edate-timedelta(days=1),freq='d')
data = {"Dates": Dates}
subdf = pd.DataFrame(data,columns=["Dates"])


subdf = subdf.set_index("Dates")




country_names = vaccines.country.unique()
for i in range(len(country_names)):
    subdf[country_names[i]] = ""




for i in range(len(vaccines.country)):
    nation = vaccines.country[i]
    index = vaccines.date[i]
    
    subdf.loc[index,nation] = vaccines.loc[i,"total_vac"]



subdf = subdf.replace(r'^\s*$', np.nan, regex=True)



indexes = subdf.index
columns = subdf.columns
for i in columns:
    if pd.isna(subdf.loc[indexes[0],i]):
        subdf.loc[indexes[0],i] = 0



for i in columns:
    for j in range(1,len(indexes)):
        if pd.isna(subdf.loc[indexes[j],i]):
            num = j-1
            subdf.loc[indexes[j],i] = subdf.loc[indexes[num],i]


                                                    



emptyrow = {}
for i in subdf.columns:
    emptyrow[i] = 0
subdf = subdf.append(emptyrow,ignore_index = True)
sub_index = subdf.index



sub_len = len(sub_index) - 1
dellist = []
for con in subdf.columns:
    try:
        country_code = pc.country_name_to_country_alpha2(con, cn_name_format="default")
        continent_name = pc.country_alpha2_to_continent_code(country_code)
        subdf.loc[sub_index[sub_len],con] = continent_name
    except:
        dellist.append(con)
        pass
for item in dellist:
    del subdf[item]



start = sdate   # start date
end = edate + timedelta(1)
finaldates = pd.date_range(start,end-timedelta(days=1),freq='d')
finaldata = {"Dates": finaldates}
def getcontinent(code):
    tester = subdf.copy(deep=True)
    for con in subdf.columns:
        if subdf.loc[sub_index[sub_len],con] != code:
            del tester[con]
    tester.drop(tester.index[-1],inplace=True)
    tester.insert(0, "Dates", finaldata["Dates"])
    tester.set_index("Dates",inplace=True)
    return tester


Africa = getcontinent("AF")
North_America = getcontinent("NA")
South_America = getcontinent("SA")
Oceania = getcontinent("OC")
Asia = getcontinent("AS")
Europe = getcontinent("EU")

Oceania = Oceania.astype(int)

home += "/" + "Oceania.mp4"


bcr.bar_chart_race(df=Oceania,
                    filename = home,
                    steps_per_period = 30,
                    title= "Oceania Covid-19 Vaccinations",
                    bar_size = 0.5,
                    bar_label_size = 7,
                    tick_label_size = 7
                )
