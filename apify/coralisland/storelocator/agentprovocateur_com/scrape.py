from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import datetime

DOMAIN = "agentprovocateur.com"
LOCATION_URL = "https://www.agentprovocateur.com/us_en/store-finder"
API_URL = "https://www.agentprovocateur.com/int_en/api/n/bundle"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-NewRelic-ID": "VQcFV1FVARAJXFNQDgcG",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def fetch_data():
    log.info("Fetching store_locator data")
    p = 0
    formdata = '{"requests":[{"action":"find","type":"store","verbosity":1,"filter":{"verbosity":1,"id":{"$nin":[]}},"children":[{"_reqId":0}]}]}'
    loclist = session.post(API_URL, headers=HEADERS, data=formdata).json()["catalog"]
    hourd = {
        "0": "Mon",
        "1": "Tues",
        "2": "Wed",
        "3": "Thurs",
        "4": "Fri",
        "5": "Sat",
        "6": "Sun",
    }
    for loc in loclist:
        if loc["country_id"] == "US":
            location_name = loc["store_name"]
            street_address = loc["address"]
            city = loc["city"]
            state = MISSING
            latitude = loc["latitude"]
            longitude = loc["longitude"]
            zip_postal = loc["postcode"]
            phone = loc["phone"]
            location_type = loc["type"]
            hourlist = str(loc["days"])
            store_number = loc["id"]
            check = 0
            flag = 0
            hours = ""
            while True:
                try:
                    hr = hourlist.split("'", 1)[1].split("'", 1)[0]
                    hrt, temp = hourlist.split(": {", 1)[1].split(", 'open_break'", 1)
                    hrt = "{" + hrt.replace("'", '"') + "}"
                    hrt = json.loads(hrt)

                    yr, month, dt = hr.split("-")
                    today = datetime.datetime((int)(yr), (int)(month), (int)(dt))
                    tdat = today.weekday()
                    daynow = hourd[str(tdat)]
                    if check == tdat:
                        break
                    if flag == 0:
                        flag = 1
                        check = tdat

                    close = (int)(hrt["close"].split(":")[0])
                    if close > 12:
                        close = close - 12
                    opent = (int)(hrt["open"].split(":")[0])
                    if opent > 12:
                        opent = opent - 12
                    hours = (
                        hours
                        + daynow
                        + ":"
                        + str(opent)
                        + " AM"
                        + " - "
                        + str(close)
                        + " PM, "
                    )
                    hourlist = temp.split("},", 1)[1]
                except:
                    break
            hours_of_operation = hours.rstrip(",")
            country_code = "US"
            log.info("Append {} => {}".format(location_name, street_address))
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=LOCATION_URL,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )
            p += 1


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
