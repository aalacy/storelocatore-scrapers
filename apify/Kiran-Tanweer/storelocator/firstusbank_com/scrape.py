from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

session = SgRequests()
website = "firstusbank.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://firstusbank.com/"
MISSING = SgRecord.MISSING

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=100,
    max_search_results=15,
)


def fetch_data():
    store_types = ["branches", "atms"]
    for lat, lng in search:
        for types in store_types:
            url = "https://www.fusb.com/_/api/{types}/{lat}/{lng}/250".format(
                lat=lat, lng=lng, types=types
            )
            stores_req = session.get(url, headers=headers).json()
            if types == "atms":
                stores_req = stores_req["atms"]
            else:
                stores_req = stores_req["branches"]
            for store in stores_req:
                title = store["name"]
                street = store["address"]
                city = store["city"]
                state = store["state"]
                pcode = store["zip"]
                lat = store["lat"]
                lng = store["long"]
                if types == "branches":
                    phone = store["phone"].strip()
                    raw_hours = store["description"].strip()
                    raw_hours = raw_hours.replace(
                        '<div><span style="font-weight: 600;">Lobby &amp; Drive Thru Hours:&nbsp;</span></div><div>',
                        "",
                    )
                    raw_hours = raw_hours.replace("</div><div>", " ")
                    raw_hours = raw_hours.replace(
                        "<div><b>Lobby &amp; Drive Thru Hours:&nbsp;</b> ", ""
                    )
                    raw_hours = raw_hours.replace("<br>", "")
                    raw_hours = raw_hours.replace(
                        "<div><b>Lobby &amp; Drive Thru Hours:</b>&nbsp; ", ""
                    )
                    hours = raw_hours.replace("</div>", "").strip()
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                else:
                    phone = "<MISSING>"
                    hours = "<MISSING>"

                if street == "100W.EmoryRoad":
                    street = "100W. Emory Road"
                if street == "8710Highway69South":
                    street = "8710 Highway 69 South"
                if street == "2619UniversityBlvd":
                    street = "2619 University Blvd"

                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url="https://www.fusb.com/resources/locations",
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=pcode,
                    country_code="US",
                    store_number=MISSING,
                    phone=phone,
                    location_type=types,
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
