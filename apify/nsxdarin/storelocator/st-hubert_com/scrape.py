from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import datetime

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("st-hubert_com")


def fetch_data():
    locs = []
    session = SgRequests(dont_retry_status_codes=([404]))
    url = "https://api.st-hubert.com/CaraAPI/APIService/getStoreList?from=60.000,-150.000&to=39.000,-50.000&eCommOnly=N"
    r = session.get(url, headers=headers)
    website = "st-hubert.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines():
        if '"storeNumber":' in line:
            sid = line.split('"storeNumber":')[1].split(",")[0].strip()
            locs.append(
                "https://api.st-hubert.com/CaraAPI/APIService/getStoreDetails?storeNumber="
                + sid
                + "&numberOfStoreHours=7"
            )
    for loc in locs:
        time.sleep(3)
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
        session = SgRequests(dont_retry_status_codes=([404]))
        r2 = session.get(loc, headers=headers)
        store_json = r2.json()
        hours_list = []
        try:
            hours_json_list = store_json["response"]["responseContent"]["hours"]
            for h in hours_json_list:
                day = datetime.datetime.strptime(h["date"], "%Y-%m-%d").strftime("%A")
                if h["store"]["available"]:
                    tim = h["store"]["open"] + " - " + h["store"]["close"]
                else:
                    tim = "Closed"

                hours_list.append(day + ":" + tim)
        except:
            pass

        hours = "; ".join(hours_list).strip()

        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines()
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

        if city == "":
            city = name.rsplit(" ", 1)[1]
        if purl == "":
            purl = "https://www.kelseys.ca/en/locations.html"
        if store != "9999":
            yield SgRecord(
                locator_domain=website,
                page_url=purl,
                location_name=name.replace("\\u0027", "'"),
                street_address=add,
                city=city.replace("\\u0027", "'"),
                state=state,
                zip_postal=zc,
                country_code=country,
                store_number=store,
                phone=phone,
                location_type=typ,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
