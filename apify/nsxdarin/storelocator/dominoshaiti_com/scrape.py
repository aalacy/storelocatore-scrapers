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

logger = SgLogSetup().get_logger("dominoshaiti_com")


def fetch_data():
    url = "http://www.dominoshaiti.com/adresse.htm"
    r = session.get(url, headers=headers)
    website = "dominoshaiti.com"
    typ = "<MISSING>"
    country = "HT"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    zc = "<MISSING>"
    lng = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<strong><span class="style33">' in line:
            name = line.split('<strong><span class="style33">')[1].split("<")[0]
            add = name
        if 'BodyTextForm">' in line:
            phone = line.split('BodyTextForm">')[1].split(" /")[0].strip()
            if "</strong>" in phone:
                phone = phone.split("</strong>")[1].strip()
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
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
