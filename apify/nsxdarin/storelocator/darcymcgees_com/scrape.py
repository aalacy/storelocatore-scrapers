from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()

logger = SgLogSetup().get_logger("darcymcgees_com")


def fetch_data():
    website = "darcymcgees.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    loc = "https://sheets.googleapis.com/v4/spreadsheets/1idWVGZkrRLTEkm6eB0baD9J7G6u-4rLIud4BL52Md3Q/values/1Stores?key=AIzaSyCWzsoRvbqZ_ilWyJ2z88O4nps4oGU5idU"
    headers = {
        "authority": "sheets.googleapis.com",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "origin": "https://www.darcymcgees.com",
        "x-client-data": "CK+1yQEIkrbJAQiktskBCKmdygEI7/LLAQi0+MsBCJ75ywEI+PnLAQi+/ssBCJ7/ywEYjp7LAQ==",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.darcymcgees.com/",
        "accept-language": "en-US,en;q=0.9",
    }
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
    r2 = session.get(loc, headers=headers)
    for item in json.loads(r2.content)["values"]:
        if item[0] != "storeNumber" and item[0] != "":
            store = item[0]
            name = item[1]
            lat = item[2]
            lng = item[3]
            add = item[5] + " " + item[6] + " " + item[7]
            city = item[8].strip()
            state = item[9]
            zc = item[10]
            phone = item[11]
            hours = item[14]
            hours = hours.replace("\n", "").replace("|", "; ").replace(" ;", ";")
            hours = hours.replace("<br>", "").replace("<b>", "")
            if "HAPPY" in hours:
                hours = hours.split("HAPPY")[0].strip()
            purl = (
                "https://www.fionnmaccools.com/en/locations/"
                + store
                + "/"
                + city.lower()
                + "-"
                + item[6].replace(" ", "-").lower()
                + ".html"
            )
            if "permanently closed" not in hours:
                yield SgRecord(
                    locator_domain=website,
                    page_url=purl,
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
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
