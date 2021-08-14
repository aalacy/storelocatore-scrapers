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

logger = SgLogSetup().get_logger("kellyservices_co_uk")


def fetch_data():
    locs = ["https://www.kellyservices.co.uk/branches/newcastle"]
    url = "https://www.kellyservices.co.uk/branches/"
    r = session.get(url, headers=headers)
    website = "kellyservices.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="https://www.kellyservices.co.uk/branches/' in line:
            items = line.split("https://www.kellyservices.co.uk/branches/")
            for item in items:
                if '<table style="border-collapse:collapse">' not in item:
                    locs.append(
                        "https://www.kellyservices.co.uk/branches/" + item.split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "<h4>Address</h4>" in line2:
                add = (
                    line2.split("<h4>Address</h4>")[1]
                    .replace("\n", "")
                    .replace("\r", "")
                    .strip()
                )
            if '<h1 class="page-title ">' in line2:
                name = line2.split('<h1 class="page-title ">')[1].split("<")[0]
            if '"item__link">' in line2:
                city = line2.split('"item__link">')[1].split("<")[0]
            if '"item__postcode">' in line2:
                zc = line2.split('"item__postcode">')[1].split("<")[0]
            if 'phone" href="tel:' in line2:
                phone = (
                    line2.split('phone" href="tel:')[1]
                    .split('"')[0]
                    .strip()
                    .replace("\t", "")
                )
            if "www.google.com/maps/" in line2:
                lat = line2.split("!3d")[1].split("!")[0]
                lng = line2.split("!2d")[1].split("!")[0]
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
