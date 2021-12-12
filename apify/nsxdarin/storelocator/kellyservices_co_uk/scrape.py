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
        if 'a  href="/branches/' in line and "branches/united-kingdom" not in line:
            locs.append(
                "https://www.kellyservices.co.uk/branches/"
                + line.split('a  href="/branches/')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<p class="address">' in line2:
                add = (
                    line2.split('<p class="address">')[1]
                    .split("</p>")[0]
                    .replace(
                        '<i class="fa fa-map-marker fa-fw" aria-hidden="true"></i>', ""
                    )
                    .strip()
                )
            if '<h1 class="page-title ">' in line2:
                name = line2.split('<h1 class="page-title ">')[1].split("<")[0]
            if '<p class="city">' in line2:
                city = line2.split('<p class="city">')[1].split("<")[0]
            if '<p class="postcode">' in line2:
                zc = line2.split('<p class="postcode">')[1].split("<")[0]
            if '"tel" href="tel:' in line2:
                phone = (
                    line2.split('"tel" href="tel:')[1]
                    .split('"')[0]
                    .strip()
                    .replace("\t", "")
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
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
