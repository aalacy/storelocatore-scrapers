from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ysl_com")


def fetch_data():
    ccodes = []
    url_home = "https://www.ysl.com/en-us/storelocator"
    r = session.get(url_home, headers=headers)
    Found = False
    for line in r.iter_lines():
        if "SELECT A REGION" in line:
            Found = True
        if Found and '<option value="' in line and "SELECT A REGION" not in line:
            ccodes.append(line.split('<option value="')[1].split('"')[0])
        if Found and '<div class="c-form__error"></div>' in line:
            Found = False
    website = "ysl.com"
    typ = "<MISSING>"
    for ccode in ccodes:
        url = (
            "https://www.ysl.com/on/demandware.store/Sites-SLP-NOAM-Site/en_US/Stores-FindStoresData?countryCode="
            + ccode
        )
        r = session.get(url, headers=headers)
        country = ccode
        logger.info("Pulling Country %s" % ccode)
        for item in json.loads(r.content)["storesData"]["stores"]:
            store = item["ID"]
            name = item["name"]
            add = item["address1"]
            city = item["city"]
            zc = item["postalCode"]
            state = item["stateCode"]
            try:
                phone = item["phone"]
            except:
                phone = "<MISSING>"
            lat = item["latitude"]
            lng = item["longitude"]
            loc = item["detailsUrl"]
            hours = "Sun: " + item["sunHours"]
            hours = hours + "; Mon: " + item["monHours"]
            hours = hours + "; Tue: " + item["tueHours"]
            hours = hours + "; Wed: " + item["wedHours"]
            hours = hours + "; Thu: " + item["thuHours"]
            hours = hours + "; Fri: " + item["friHours"]
            hours = hours + "; Sat: " + item["satHours"]
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
