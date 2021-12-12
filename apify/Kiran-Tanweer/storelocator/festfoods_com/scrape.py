from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import os

os.environ["PROXY_URL"] = "http://groups-BUYPROXIES94952:{}@proxy.apify.com:8000/"
os.environ["PROXY_PASSWORD"] = "apify_proxy_4j1h689adHSx69RtQ9p5ZbfmGA3kw12p0N2q"

session = SgRequests()
website = "festfood_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.festfood.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.festfoods.com/api/freshop/1/stores?sort=name&name_sort=asc&app_key=festival_foods_envano"
        r = session.get(url, headers=headers).json()
        r = r["items"]
        for loc in r:
            ids = loc["id"].strip()
            if ids != "3322" and ids != "1955" and ids != "100":
                title = loc["name"]
                street = loc["address_1"]
                city = loc["city"]
                state = loc["state"]
                pcode = loc["postal_code"]
                lat = loc["latitude"]
                lng = loc["longitude"]
                storeid = loc["store_number"]
                try:
                    link = loc["url"]
                except KeyError:
                    link = "<MISSING>"
                try:
                    phone = loc["phone"]
                except KeyError:
                    phone = "<MISSING>"

                if state == "Wisconsin":
                    state = "WI"

            if link != "https://www.festfoods.com/stores/weston":

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=storeid,
                    phone=phone,
                    location_type=MISSING,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation="<INACCESSIBLE>",
                )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
