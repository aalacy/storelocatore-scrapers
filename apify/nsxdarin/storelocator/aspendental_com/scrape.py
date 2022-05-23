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

logger = SgLogSetup().get_logger("aspendental_com")


def fetch_data():
    locs = []
    for x in range(0, 1250, 50):
        logger.info(str(x))
        url = (
            "https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?experienceKey=aspen_dental_answers&api_key=5568aa1809f16997ec2ac0c1ed321f59&v=20190101&version=PRODUCTION&locale=en&input=dentist+near+me&verticalKey=locations&limit=50&offset="
            + str(x)
            + "&facetFilters=%7B%7D&session_id=203a4345-5104-4f2e-92d1-b0978f41dcd0&sessionTrackingEnabled=true&sortBys=%5B%5D&referrerPageUrl=https%3A%2F%2Fwww.aspendental.com%2F&source=STANDARD&jsLibVersion=v1.12.0"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if ',"c_profileURL":"' in line:
                items = line.split(',"c_profileURL":"')
                for item in items:
                    if '{"meta":{"' not in item:
                        lurl = item.split('"')[0]
                        locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        website = "aspendental.com"
        typ = "<MISSING>"
        country = "US"
        hours = ""
        OFound = False
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if '"latitude": "' in line:
                lat = line.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line:
                lng = line.split('"longitude": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if "'officeName':'" in line:
                store = line.split("'facilityNumber':'")[1].split("'")[0]
                city = line.split("'addressLocality':'")[1].split("'")[0]
                state = line.split("'addressRegion':'")[1].split("'")[0]
                zc = line.split("'postalCode':'")[1].split("'")[0]
                add = line.split("'streetAddress':'")[1].split("'")[0]
                phone = line.split("'telephone':'")[1].split("'")[0]
            if '<span class="text-day">' in line and OFound:
                day = line.split('<span class="text-day">')[1].split("<")[0]
            if '<strong class="title">Office hours</strong>' in line:
                OFound = True
            if OFound and 'lass="scheduling-title">' in line:
                OFound = False
            if OFound and '<span class="text-info">' in line:
                hrs = (
                    day + ": " + line.split('<span class="text-info">')[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        name = name.replace("&amp;", "&")
        if "/5304-hickory-hollow-lane" not in loc:
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
