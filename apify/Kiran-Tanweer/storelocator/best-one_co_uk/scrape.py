from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicZipSearch

session = SgRequests()
website = "best-one_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://stores.best-one.co.uk",
    "Connection": "keep-alive",
    "Referer": "https://stores.best-one.co.uk/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "Cookie": "__cf_bm=PTqLLokKoAp5f0Xwbf5css_1j79BHCcT6f7AdRtMG5o-1636391251-0-AVSaPrK2rIVdARjoNuAvJMky9Gwd016aOcELZX3FsLmsTD3YL2AwWNj5CkbWsk9lii+Y5eFV+FweeYVn8zA+d+3cxtX5zOWRXrc2ugW80Stx",
}

DOMAIN = "https://www.best-one.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search = DynamicZipSearch(country_codes=["GB"])
        for zipcode in search:
            search_url = (
                "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=5&location="
                + zipcode
                + "&limit=50&api_key=e9ab7db1797db4fe63c8c584a7c162ff&v=20181201&resolvePlaceholders=true&entityTypes=location&searchIds=4459"
            )
            stores_req = session.get(search_url, headers=headers).json()
            stores_req = stores_req["response"]["entities"]
            if stores_req != []:
                for store in stores_req:
                    script = str(store)
                    street = store["address"]["line1"]
                    city = store["address"]["city"]
                    country = store["address"]["countryCode"]
                    pcode = store["address"]["postalCode"]
                    state = MISSING
                    title = store["name"]
                    if script.find("geocodedCoordinate") != -1:
                        coords = store["geocodedCoordinate"]
                        lat = coords["latitude"]
                        lng = coords["longitude"]
                    else:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    storeid = store["meta"]["id"]
                    hours = store["hours"]
                    url = store["landingPageUrl"]
                    if script.find("mainPhone") != -1:
                        phone = store["mainPhone"]
                    else:
                        phone = "<MISSING>"
                    try:
                        mon = hours["monday"]["openIntervals"][0]
                        mon = "Monday " + mon["start"] + "-" + mon["end"]
                    except KeyError:
                        mon = hours["monday"]["isClosed"]
                        if mon is True:
                            mon = "Closed"

                    try:
                        tues = hours["tuesday"]["openIntervals"][0]
                        tues = "Tuesday " + tues["start"] + "-" + tues["end"]
                    except KeyError:
                        tues = hours["tuesday"]["isClosed"]
                        if tues is True:
                            tues = "Closed"

                    try:
                        wed = hours["wednesday"]["openIntervals"][0]
                        wed = "Wednesday " + wed["start"] + "-" + wed["end"]
                    except KeyError:
                        wed = hours["wednesday"]["isClosed"]
                        if wed is True:
                            wed = "Closed"

                    try:
                        thurs = hours["thursday"]["openIntervals"][0]
                        thurs = "Thursday " + thurs["start"] + "-" + thurs["end"]
                    except KeyError:
                        thurs = hours["thursday"]["isClosed"]
                        if thurs is True:
                            thurs = "Closed"

                    try:
                        fri = hours["friday"]["openIntervals"][0]
                        fri = "Friday " + fri["start"] + "-" + fri["end"]
                    except KeyError:
                        fri = hours["friday"]["isClosed"]
                        if fri is True:
                            fri = "Closed"

                    try:
                        sat = hours["saturday"]["openIntervals"][0]
                        sat = "Saturday " + sat["start"] + "-" + sat["end"]
                    except KeyError:
                        sat = hours["saturday"]["isClosed"]
                        if sat is True:
                            sat = "Closed"

                    try:
                        sun = hours["sunday"]["openIntervals"][0]
                        sun = "Sunday " + sun["start"] + "-" + sun["end"]
                    except KeyError:
                        sun = hours["sunday"]["isClosed"]
                        if sun is True:
                            sun = "Closed"
                    hoo = (
                        mon
                        + " "
                        + tues
                        + " "
                        + wed
                        + " "
                        + thurs
                        + " "
                        + fri
                        + " "
                        + sat
                        + " "
                        + sun
                    )

                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=url,
                        location_name=title,
                        street_address=street.strip(),
                        city=city.strip(),
                        state=state,
                        zip_postal=pcode,
                        country_code=country,
                        store_number=storeid,
                        phone=phone,
                        location_type=MISSING,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hoo,
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
