from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "authority": "sheets.googleapis.com",
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "accept": "application/json, text/javascript, */*; q=0.01",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "origin": "https://www.milestonesrestaurants.com",
    "x-client-data": "CK+1yQEIkrbJAQiktskBCKmdygEI7/LLAQi0+MsBCJ75ywEI+PnLAQi+/ssBCJ7/ywEYjp7LAQ==",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.milestonesrestaurants.com/",
    "accept-language": "en-US,en;q=0.9",
}

logger = SgLogSetup().get_logger("milestonesrestaurants_com")


def fetch_data():
    locs = []
    url = "https://www.milestonesrestaurants.com/en/locations.html"
    r = session.get(url, headers=headers)
    website = "milestonesrestaurants.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'spreadsheetID: "' in line:
            sid = line.split(': "')[1].split('"')[0].replace("\\u002D", "-")
            locs.append(
                "https://sheets.googleapis.com/v4/spreadsheets/"
                + sid
                + "/values/1Stores?key=AIzaSyCWzsoRvbqZ_ilWyJ2z88O4nps4oGU5idU"
            )
    for loc in locs:
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
                purl = (
                    "https://www.milestonesrestaurants.com/en/locations/"
                    + store
                    + "/"
                    + city.lower()
                    + "-"
                    + item[6].replace(" ", "-").lower()
                    + ".html"
                )
                if ";  Brunch" in hours:
                    hours = hours.split(";  Brunch")[0]
                if "; Brunch" in hours:
                    hours = hours.split("; Brunch")[0]
                if "; Happy" in hours:
                    hours = hours.split("; Happy")[0]
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
