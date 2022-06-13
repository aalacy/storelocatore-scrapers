from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("americansignaturefurniture_com")


def fetch_data():
    url = (
        "https://api.blueport.com/v1/store?key=AIzaSyA6L31EabD8yXrytC4YBOoEdbNfbfDhjtw"
    )
    r = session.get(url, headers=headers)
    website = "americansignaturefurniture.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"storeKey":"' in line:
            items = line.split('{"storeKey":"')
            for item in items:
                if "storeName" in item:
                    store = item.split('"')[0]
                    name = item.split('"storeName":"')[1].split('"')[0]
                    add = item.split('"thoroughfare":"')[1].split('"')[0]
                    city = item.split('"locality":"')[1].split('"')[0]
                    state = item.split('"administrativeArea":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    try:
                        phone = item.split('"telephone":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    try:
                        loc = (
                            "https://www.americansignaturefurniture.com"
                            + item.split('"storeUrl":"')[1].split('"')[0]
                        )
                    except:
                        loc = "<MISSING>"
                    try:
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    try:
                        days = item.split('{"day":"')
                        hours = ""
                        for day in days:
                            if ',"storeHours":"' in day:
                                hrs = (
                                    day.split('"')[0]
                                    + ": "
                                    + day.split(',"storeHours":"')[1].split('"')[0]
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    except:
                        hours = "<MISSING>"
                    if lat != "<MISSING>":
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
