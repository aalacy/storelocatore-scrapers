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

logger = SgLogSetup().get_logger("crowneplaza_co_uk")


def fetch_data():
    locs = []
    states = []
    alllocs = []
    url = "https://www.ihg.com/crowneplaza/destinations/gb/en/united-kingdom-hotels"
    r = session.get(url, headers=headers)
    website = "crowneplaza.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "Hotels</span></a>" in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if ',"@type":"Hotel","name":"Crowne Plaza' in line2:
                locs.append(line2.split('"url":"')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '"og:title" content="' in line2:
                name = line2.split('"og:title" content="')[1].split('"')[0]
            if 'location:latitude"  content="' in line2:
                lat = line2.split('location:latitude"  content="')[1].split('"')[0]
            if 'location:longitude" content="' in line2:
                lng = line2.split('location:longitude" content="')[1].split('"')[0]
            if "|  United Kingdom |" in line2:
                add = line2.split("|")[0].strip().replace("\t", "").split(",")[0]
                city = line2.split("|")[0].split(",")[1].strip().replace("\t", "")
                state = "<MISSING>"
                zc = line2.split("|")[1].strip().replace("\t", "")
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
        if loc not in alllocs:
            alllocs.append(loc)
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
