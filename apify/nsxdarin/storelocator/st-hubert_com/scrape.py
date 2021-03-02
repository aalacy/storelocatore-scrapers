import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup
import datetime
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("st-hubert_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def fetch_data():
    locs = []
    url = "https://api.st-hubert.com/CaraAPI/APIService/getStoreList?from=60.000,-150.000&to=39.000,-50.000&eCommOnly=N"
    r = session.get(url, headers=headers)
    website = "st-hubert.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if '"storeNumber":' in line:
            sid = line.split('"storeNumber":')[1].split(",")[0].strip()
            locs.append(
                "https://api.st-hubert.com/CaraAPI/APIService/getStoreDetails?storeNumber="
                + sid
                + "&numberOfStoreHours=7"
            )
    for loc in locs:
        time.sleep(2)
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        purl = ""
        weekday = ""
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"name": "storeUrlSlug_EN",' in line2:
                g = next(lines)
                purl = (
                    "https://www.st-hubert.com/en/restaurants/"
                    + g.split('"value": "')[1].split('"')[0]
                    + ".html"
                )
            if '"storeNumber": ' in line2:
                store = line2.split('"storeNumber": ')[1].split(",")[0]
            if '"storeName": "' in line2:
                name = line2.split('"storeName": "')[1].split('"')[0]
            if 'streetNumber": ' in line2:
                add = line2.split('streetNumber": ')[1].split(",")[0].replace('"', "")
            if 'street": "' in line2:
                add = add + " " + line2.split('street": "')[1].split('"')[0]
            if '"city": "' in line2:
                city = line2.split('"city": "')[1].split('"')[0]
            if '"province": "' in line2:
                state = line2.split('"province": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"phoneNumber": "' in line2:
                phone = line2.split('"phoneNumber": "')[1].split('"')[0]
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(",")[0]
            if '"longitude": ' in line2:
                lng = line2.split('"longitude": ')[1].split(",")[0]
            if '"date": "' in line2:
                day = line2.split('"date": "')[1].split('"')[0]
                dt = day
                year, month, dday = (int(x) for x in dt.split("-"))
                ans = datetime.date(year, month, dday)
                weekday = ans.strftime("%A")
            if '"store": {' in line2:
                g = next(lines)
                hrs = weekday + ": " + g.split(': "')[1].split('"')[0]
                hrs = hrs + "-" + next(lines).split(': "')[1].split('"')[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if zc == "":
            zc = "<MISSING>"
        if city == "":
            city = name.rsplit(" ", 1)[1]
        yield [
            website,
            purl,
            name,
            add,
            city,
            state,
            zc,
            country,
            store,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
