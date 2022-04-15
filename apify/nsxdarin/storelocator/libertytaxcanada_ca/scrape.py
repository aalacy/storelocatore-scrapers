from sgrequests import SgRequests
import time
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("libertytaxcanada_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.libertytaxcanada.ca/api/franchise/getAllFranchise/get-all-franchise"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '{"officeCode":"' in line:
            items = line.split('{"officeCode":"')
            for item in items:
                if '"label":"' in item:
                    locs.append(
                        "https://www.libertytaxcanada.ca/income-tax-preparation-locations/"
                        + item.split('"')[0]
                    )
    for loc in locs:
        lurl = (
            "https://www.libertytaxcanada.ca/api/franchise/getFranchise/"
            + loc.rsplit("/", 1)[1]
        )
        time.sleep(5)
        logger.info(("Pulling Location %s..." % loc))
        website = "libertytaxcanada.ca"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "CA"
        zc = ""
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        store = ""
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            if "officeCode" in line2 and '"active":"true"' in line2:
                store = line2.split('"officeCode":"')[1].split('"')[0]
                name = line2.split('"label":"')[1].split('"')[0]
                add = line2.split('"street":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                days = line2.split('{"day":"')
                for day in days:
                    if '"open":"' in day:
                        if '"closed":"00:00"' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"open":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closed":"')[1].split('"')[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if store != "":
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
