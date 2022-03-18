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
website = "asics_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://asics.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://www.locally.com/stores/conversion_data?has_data=true&company_id=1682&store_mode=&style=&color=&upc=&category=&inline=1&show_links_in_list=&parent_domain=&map_center_lat=40.754377699800074&map_center_lng=-111.8836100000002&map_distance_diag=3000&sort_by=proximity&no_variants=0&only_retailer_id=&dealers_company_id=&only_store_id=false&uses_alt_coords=false&q=false&zoom_level="
        stores_req = session.get(search_url, headers=headers).json()
        stores_req = stores_req["markers"]
        for store in stores_req:
            storeid = store["id"]
            title = store["name"]
            lat = store["lat"]
            lng = store["lng"]
            street = store["address"]
            city = store["city"]
            state = store["state"]
            pcode = store["zip"]
            phone = store["phone"]
            country = store["country"]
            sun = (
                "Sun:"
                + " "
                + str(store["sun_time_open"])
                + "-"
                + str(store["sun_time_close"])
            )
            mon = (
                "Mon:"
                + " "
                + str(store["mon_time_open"])
                + "-"
                + str(store["mon_time_close"])
            )
            tues = (
                "Tues:"
                + " "
                + str(store["tue_time_open"])
                + "-"
                + str(store["tue_time_close"])
            )
            wed = (
                "Wed:"
                + " "
                + str(store["wed_time_open"])
                + "-"
                + str(store["wed_time_close"])
            )
            thurs = (
                "Thurs:"
                + " "
                + str(store["thu_time_open"])
                + "-"
                + str(store["thu_time_close"])
            )
            fri = (
                "Fri:"
                + " "
                + str(store["fri_time_open"])
                + "-"
                + str(store["fri_time_close"])
            )
            sat = (
                "Sat:"
                + " "
                + str(store["sat_time_open"])
                + "-"
                + str(store["sat_time_close"])
            )
            hours = (
                mon
                + " "
                + tues
                + " "
                + wed
                + " "
                + thurs
                + ""
                + fri
                + " "
                + sat
                + " "
                + sun
            )

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=DOMAIN,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=country,
                store_number=storeid,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
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
