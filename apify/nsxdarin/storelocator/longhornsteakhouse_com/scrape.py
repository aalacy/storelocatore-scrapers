import re
import time
import random
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgselenium import SgChrome
from tenacity import retry, stop_after_attempt
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

alllocs = []

logger = SgLogSetup().get_logger("longhornsteakhouse_com")
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authority": "www.longhornsteakhouse.com",
    "scheme": "https",
    "cache-control": "max-age=0",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "method": "GET",
}


def sleep():
    time.sleep(random.randint(4, 7))


def fetch(loc, driver):
    return driver.execute_async_script(
        f"""
        var done = arguments[0]
        fetch("{loc}")
            .then(res => res.text())
            .then(done)
    """
    )


@retry(stop=stop_after_attempt(3))
def fetch_location(loc, driver):
    PhoneFound = False
    count = 1
    while PhoneFound is False and count <= 15:
        count = count + 1
        try:
            logger.info("Pulling Location %s..." % loc)
            website = "longhornsteakhouse.com"
            typ = "Restaurant"
            hours = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            phone = ""
            lat = ""
            lng = ""
            hours = ""
            country = ""
            name = ""
            store = loc.rsplit("/", 1)[1]

            text = fetch(loc, driver)
            sleep()

            if re.search("access denied", text, re.IGNORECASE):
                raise Exception()

            text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
            if 'id="restLatLong" value="' in text:
                lat = text.split('id="restLatLong" value="')[1].split(",")[0]
                lng = (
                    text.split('id="restLatLong" value="')[1]
                    .split(",")[1]
                    .split('"')[0]
                )
            if '"weekda' in text:
                day = text.split('"weekda')[1].split('">')[1].split("<")[0]
                if "(" in day:
                    day = day.split("(")[1].split(")")[0]
            if "<title>" in text:
                name = text.split("<title>")[1].split(" |")[0]
            if 'id="restAddress" value="' in text:
                add = text.split('id="restAddress" value="')[1].split(",")[0]
                city = text.split('id="restAddress" value="')[1].split(",")[1]
                state = text.split('id="restAddress" value="')[1].split(",")[2]
                zc = (
                    text.split('id="restAddress" value="')[1]
                    .split(",")[3]
                    .split('"')[0]
                )
                country = "US"
            if '"streetAddress":"' in text:
                if add == "":
                    add = text.split('"streetAddress":"')[1].split('"')[0]
                    country = text.split('"addressCountry":"')[1].split('"')[0]
                    city = text.split('"addressLocality":"')[1].split('"')[0]
                    state = text.split('"addressRegion":"')[1].split('"')[0]
                    zc = text.split('"postalCode":"')[1].split('"')[0]
                if lat == "":
                    try:
                        lat = text.split('"latitude":"')[1].split('"')[0]
                        lng = text.split('"longitude":"')[1].split('"')[0]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
            if '"openingHours":["' in text:
                hours = (
                    text.split('"openingHours":["')[1]
                    .split('"]')[0]
                    .replace('","', "; ")
                )
            if ',"telephone":"' in text:
                phone = text.split(',"telephone":"')[1].split('"')[0]
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if hours == "<MISSING>":
                hours = "<INACCESSIBLE>"
            if phone != "<MISSING>":
                PhoneFound = True
                if loc not in alllocs:
                    alllocs.append(loc)
                    if "Find A R" not in name:
                        return SgRecord(
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
        except:
            PhoneFound = False


def fetch_data():
    locs = []
    url = "https://www.longhornsteakhouse.com/locations-sitemap.xml"
    session = SgRequests()
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.longhornsteakhouse.com/locations/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)

    with ThreadPoolExecutor(max_workers=1) as executor, SgChrome() as driver:
        driver.get("https://www.longhornsteakhouse.com/locations/")
        futures = [executor.submit(fetch_location, loc, driver) for loc in locs]
        for future in as_completed(futures):
            poi = future.result()
            if poi:
                yield poi


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
