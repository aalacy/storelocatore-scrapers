from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()

logger = SgLogSetup().get_logger("thebiermarkt_com")


def fetch_data():
    website = "thebiermarkt.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    loc = "https://sheets.googleapis.com/v4/spreadsheets/18uWiqCyn0VG3AKRfPF03mOipqn4nYdBu5cjSck3FvUU/values/1Stores?key=AIzaSyCWzsoRvbqZ_ilWyJ2z88O4nps4oGU5idU"
    headers = {
        "authority": "sheets.googleapis.com",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "origin": "https://www.thebiermarkt.com",
        "x-client-data": "CK+1yQEIkrbJAQiktskBCKmdygEI7/LLAQi0+MsBCJ75ywEI+PnLAQi+/ssBCJ7/ywEYjp7LAQ==",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://www.thebiermarkt.com/",
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
        if item[0] != "storeNumber":
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
            purl = "https://www.thebiermarkt.com/en/locations.html"
            if "; , storenotice" in hours:
                hours = hours.split("; , storenotice")[0].strip()
            if ", storenotice" in hours:
                hours = hours.split(", storenotice")[0].strip()
            if "Holiday" in hours:
                hours = hours.split("Holiday")[0].strip()
            if hours == "<MISSING>":
                hours = "Temporarily Closed"
            if "Esplanade" in name:
                purl = "https://www.thebiermarkt.com/en/locations/esplanade.html"
            if "Don Mills" in name:
                purl = "https://www.thebiermarkt.com/en/locations/don-mills.html"
            if "Montreal" in name:
                purl = "https://www.thebiermarkt.com/en/locations/montreal.html"
            if "Ottawa" in name:
                purl = "https://www.thebiermarkt.com/en/locations/ottawa.html"
            hours = hours.replace("\n", "").replace("|", "; ").replace(" ;", ";")
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
