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

logger = SgLogSetup().get_logger("chefstore_com")


def fetch_data():
    locs = []
    url = "https://www.chefstore.com/locations/"
    r = session.get(url, headers=headers)
    website = "chefstore.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            '<a class="button plain-button button-small" href = "/locations/store/'
            in line
        ):
            items = line.split(
                '<a class="button plain-button button-small" href = "/locations/store/'
            )
            for item in items:
                if "Store Info</a>" in item:
                    lurl = (
                        "https://www.chefstore.com/locations/store/"
                        + item.split('"')[0]
                    )
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if 'h1 class="h2 page-title no-margin">' in line:
                name = line.split('h1 class="h2 page-title no-margin">')[1].split(
                    "</h2>"
                )[0]
                name = (
                    name.replace("<sup>", "").replace("</sup>", "").replace("&reg;", "")
                )
            if '"addressLocality": "' in line:
                city = line.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line:
                state = line.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line:
                add = line.split('"streetAddress": "')[1].split('"')[0]
            if '"telephone": "' in line:
                phone = line.split('"telephone": "')[1].split('"')[0]
            if '"branchCode": "' in line:
                store = line.split('"branchCode": "')[1].split('"')[0]
            if 'name="latitude"    value="' in line:
                lat = line.split('name="latitude"    value="')[1].split('"')[0]
            if 'name="longitude"   value="' in line:
                lng = line.split('name="longitude"   value="')[1].split('"')[0]
            if '"openingHours": ["' in line:
                hours = (
                    line.split('"openingHours": ["')[1]
                    .split("]")[0]
                    .replace('","', "; ")
                    .replace('"', "")
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
