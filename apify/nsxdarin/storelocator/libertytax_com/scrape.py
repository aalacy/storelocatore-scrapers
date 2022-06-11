from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("libertytax_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    country = "US"
    website = "libertytax.com"
    typ = "<MISSING>"
    locs = []
    url = "https://www.libertytax.com/api/franchise/getAllFranchise/get-all-franchise"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '{"officeCode":"' in line:
            items = line.split('{"officeCode":"')
            for item in items:
                if '"landmark":"' in item:
                    locs.append(
                        "https://www.libertytax.com/income-tax-preparation-locations/"
                        + item.split('"')[0]
                    )
    for loc in locs:
        logger.info(loc)
        store = loc.rsplit("/", 1)[1]
        rurl = "https://www.libertytax.com/api/franchise/getFranchise/" + store
        r = session.get(rurl, headers=headers)
        for line in r.iter_lines():
            if '"label":"' in line and '"active":"false"' not in line:
                name = line.split('"label":"')[1].split('"')[0]
                add = (
                    line.split('"street":"')[1].split('"')[0]
                    + " "
                    + line.split('"street2":"')[1].split('"')[0]
                )
                add = add.strip()
                city = line.split('"city":"')[1].split('"')[0]
                state = line.split('"state":"')[1].split('"')[0]
                zc = line.split('"zip":"')[1].split('"')[0]
                try:
                    phone = line.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                hours = ""
                lat = "<MISSING>"
                lng = "<MISSING>"
                days = line.split('{"day":"')
                for day in days:
                    if ',"open":"' in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split(',"open":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closed":"')[1].split('"')[0]
                        )
                        hrs = hrs.replace("00:00-00:00", "Closed")
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
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
