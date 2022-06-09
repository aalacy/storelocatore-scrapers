from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests(verify_ssl=False)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("oxxousa_com")


def fetch_data():
    url = "https://oxxousa.com/store-locator/"
    loc = "https://oxxousa.com/store-locator/"
    r = session.get(url, headers=headers)
    website = "oxxousa.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "position%22%3A%22" in line:
            items = line.split("position%22%3A%22")
            for item in items:
                if "coordinates%22%3A%22" in item:
                    store = "<MISSING>"
                    lat = item.split("coordinates%22%3A%22")[1].split("%")[0]
                    lng = (
                        item.split("coordinates%22%3A%22")[1]
                        .split("%2C%20")[1]
                        .split("%")[0]
                    )
                    raw_address = (
                        item.split("infoAddress%22%3A%22")[1]
                        .split("%22%2C%22infoSite")[0]
                        .replace("%20", " ")
                        .replace("%2C", ",")
                        .replace("%23", "#")
                    )
                    name = (
                        item.split("infoTitle%22%3A%22")[1]
                        .split("%22")[0]
                        .replace("%20", " ")
                    )
                    add = ""
                    city = ""
                    state = ""
                    zc = ""
                    formatted_addr = parse_address_intl(raw_address)
                    add = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        add = add + ", " + formatted_addr.street_address_2
                    city = formatted_addr.city
                    state = (
                        formatted_addr.state if formatted_addr.state else "<MISSING>"
                    )
                    zc = (
                        formatted_addr.postcode
                        if formatted_addr.postcode
                        else "<MISSING>"
                    )
                    phone = (
                        item.split("nfoPhone%22%3A%22")[1]
                        .split("%22%2C%22infoEmail")[0]
                        .replace("%28", "(")
                        .replace("%29", ")")
                        .replace("%5Cu00a0", "")
                        .replace("%20", " ")
                        .strip()
                    )
                    hours = (
                        item.split("WorkingHours%22%3A%22")[1]
                        .split("%22%2C%22infoWindow")[0]
                        .replace("%20", " ")
                        .replace("%3A", ":")
                    )
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
                        raw_address=raw_address,
                        hours_of_operation=hours,
                    )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                },
                fail_on_empty_id=False,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
