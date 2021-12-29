from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time
from tenacity import retry, stop_after_attempt
import tenacity

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("hooters_com")


@retry(stop=stop_after_attempt(7), wait=tenacity.wait_fixed(7))
def get_response(url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        if response.status_code == 200:
            logger.info(f"{url} >> HTTP STATUS: {response.status_code}")
            return response
        raise Exception(f"{url} >> HTTP Error Code: {response.status_code}")


def fetch_data():
    url = "https://www.hooters.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    website = "hooters.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            "<loc>https://www.hooters.com/locations/" in line
            and "<loc>https://www.hooters.com/locations/<" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            if "3107-castleton" not in lurl:
                locs.append(lurl)
    for loc in locs:
        time.sleep(3)
        TC = False
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        country = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        store = "<MISSING>"
        phone = ""
        r2 = get_response(loc)
        for line2 in r2.iter_lines():
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if "temporarily closed" in line2:
                TC = True
            if '"c-location-meta__address-line-1">' in line2:
                add = line2.split('"c-location-meta__address-line-1">')[1].split("<")[0]
            if '"c-location-meta__address-line-2">' in line2:
                csz = line2.split('"c-location-meta__address-line-2">')[1].split("<")[0]
                if csz.count(",") == 2:
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip()
                    zc = csz.split(",")[2].strip()
                    country = "US"
                elif csz.count(",") == 1:
                    city = csz.split(",")[0]
                    zc = "<MISSING>"
                    country = csz.split(",")[1].strip()
                else:
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip()
                    zc = csz.split(",")[2].strip()
                    country = csz.split(",")[3].strip()
                if "Canada" in csz:
                    country = "CA"
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
            if '__phone-link">' in line2:
                phone = line2.split('__phone-link">')[1].split("<")[0]
            if 'c-location-hours__day">' in line2:
                day = line2.split('c-location-hours__day">')[1].split("<")[0]
            if '{"@type":"OpeningHoursSpecification",' in line2:
                try:
                    days = line2.split('{"@type":"OpeningHoursSpecification",')
                    for day in days:
                        if '"dayOfWeek":["' in day:
                            hrs = (
                                day.split('"dayOfWeek":["')[1].split('"')[0]
                                + ": "
                                + day.split('"opens":"')[1].split(':00"')[0]
                                + "-"
                                + day.split('"closes":"')[1].split(':00"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                except:
                    hours = "<MISSING>"
        if TC:
            hours = "Temporarily Closed"
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
