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

logger = SgLogSetup().get_logger("aurorahealthcare_org")


def fetch_data():
    url = "https://www.aurorahealthcare.org/sitemap.xml"
    website = "aurorahealthcare.org"
    country = "US"
    logger.info("Pulling Stores")
    for x in range(0, 2200, 10):
        locs = []
        logger.info(str(x))
        url = (
            "https://locator-api.localsearchprofiles.com/api/LocationSearchResults/?configuration=9b0e4802-0c40-43e1-ba7e-2fc225e26e24&&address=34.0683231%2C-118.4069666&searchby=address&start="
            + str(x)
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '"PinType":["' in line:
                items = line.split('"PinType":["')
                for item in items:
                    if '{"Found":' not in item:
                        locs.append(
                            item.split('"Url":["')[1].split('"')[0]
                            + "|"
                            + item.split('"')[0]
                        )
        for loc in locs:
            try:
                lurl = loc.split("|")[0]
                typ = loc.split("|")[1]
                logger.info(lurl)
                name = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                store = "<MISSING>"
                phone = ""
                lat = ""
                lng = ""
                hours = ""
                r2 = session.get(lurl, headers=headers)
                for line2 in r2.iter_lines():
                    if '"openingHours":["' in line2:
                        hours = (
                            line2.split('"openingHours":["')[1]
                            .split("]")[0]
                            .replace('","', "; ")
                            .replace('"', "")
                        )
                    if "<title>" in line2:
                        name = line2.split("<title>")[1].split("<")[0]
                        if " |" in name:
                            name = name.split(" |")[0]
                    if '"streetAddress":"' in line2:
                        add = line2.split('"streetAddress":"')[1].split('"')[0]
                    if '"addressLocality":"' in line2:
                        city = line2.split('"addressLocality":"')[1].split('"')[0]
                    if '"addressRegion":"' in line2:
                        state = line2.split('"addressRegion":"')[1].split('"')[0]
                    if '"postalCode":"' in line2:
                        zc = line2.split('"postalCode":"')[1].split('"')[0]
                    if '"telephone":"' in line2:
                        phone = line2.split('"telephone":"')[1].split('"')[0]
                    if 'data-latitude="' in line2:
                        lat = line2.split('data-latitude="')[1].split('"')[0]
                        lng = line2.split('longitude="')[1].split('"')[0]
                if hours == "":
                    hours = "<MISSING>"
                if " - " in name:
                    name = name.split(" - ")[0]
                if add != "":
                    yield SgRecord(
                        locator_domain=website,
                        page_url=lurl,
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
            except:
                pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
