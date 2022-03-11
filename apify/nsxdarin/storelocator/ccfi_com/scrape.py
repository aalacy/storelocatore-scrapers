from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

logger = SgLogSetup().get_logger("ccfi_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=100,
    max_search_results=100,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    for zipcode in search:
        logger.info(("Pulling Postal Code %s..." % zipcode))
        url = "https://www.ccfi.com/ajax/stores.php?zip=" + zipcode + "&distance=all"
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        website = "ccfi.com"
        for line in lines:
            if '{"lat":"' in line:
                items = line.split('{"lat":"')
                for item in items:
                    if '"lng":"' in item:
                        country = "US"
                        loc = "https://www.ccfi.com/locations/"
                        lng = item.split('"lng":"')[1].split('"')[0]
                        lat = item.split('"')[0]
                        add = item.split(',"street":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zip":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phone":"')[1].split('"')[0]
                        except:
                            phone = "<MISSING>"
                        try:
                            typ = item.split('"brand_link":"')[1].split('"')[0]
                        except:
                            typ = ""
                        store = "<MISSING>"
                        try:
                            hours = (
                                "Sun: "
                                + item.split('"sunday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"sunday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Mon: "
                                + item.split('"monday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"monday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Tue: "
                                + item.split('"tuesday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"tuesday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Wed: "
                                + item.split('"wednesday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"wednesday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Thu: "
                                + item.split('"thursday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"thursday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Fri: "
                                + item.split('"friday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"friday_close":"')[1].split('"')[0]
                            )
                            hours = (
                                hours
                                + "; Sat: "
                                + item.split('"saturday_open":"')[1].split('"')[0]
                                + "-"
                                + item.split('"saturday_close":"')[1].split('"')[0]
                            )
                        except:
                            hours = "<MISSING>"
                        hours = hours.replace("Closed-Closed", "Closed")
                        if typ == "":
                            typ = "ccfi"
                        name = typ.title() + " - " + city
                        if lat == "" or "." not in lat:
                            lat = "<MISSING>"
                        if lng == "" or "." not in lng:
                            lng = "<MISSING>"
                        yield SgRecord(
                            locator_domain=website,
                            page_url=loc,
                            location_name=name,
                            street_address=add,
                            city=city,
                            state=state,
                            zip_postal=zc,
                            country_code=country,
                            phone=phone,
                            location_type=typ,
                            store_number=store,
                            latitude=lat,
                            longitude=lng,
                            hours_of_operation=hours,
                        )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
