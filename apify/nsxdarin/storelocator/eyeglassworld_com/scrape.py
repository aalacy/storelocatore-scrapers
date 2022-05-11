import json

from bs4 import BeautifulSoup
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

logger = SgLogSetup().get_logger("eyeglassworld_com")


def fetch_data():
    locs = []
    url = "https://www.eyeglassworld.com/store/store_sitemap.xml"
    r = session.get(url, headers=headers)

    website = "eyeglassworld.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.eyeglassworld.com/store-list/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store_num = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""

        r2 = session.get(loc, headers=headers)
        try:
            base = BeautifulSoup(r2.text, "lxml")
        except:
            continue

        try:
            name = base.find(id="location-name").text.replace("amp;", "")
            got_name = True
        except:
            got_name = False

        if got_name:
            add = base.find(attrs={"itemprop": "streetAddress"})["content"]
            city = base.find(class_="Address-field Address-city").text
            state = base.find(attrs={"itemprop": "addressRegion"}).text
            zc = base.find(attrs={"itemprop": "postalCode"}).text
            phone = base.find(class_="Text Phone-text Phone-number").text
            hours = " ".join(
                list(base.find(class_="c-hours-details").stripped_strings)[2:]
            )
        else:
            name = base.h1.text.replace("\xa0\n", " ").strip()

            try:
                script = (
                    base.find_all("script", attrs={"type": "application/ld+json"})[-1]
                    .contents[0]
                    .strip()
                    .replace('pm",', 'pm"')
                )
                store = json.loads(script)
            except:
                script = (
                    base.find_all("script", attrs={"type": "application/ld+json"})[-1]
                    .contents[0]
                    .strip()
                )
                store = json.loads(script)

            add = store["address"]["streetAddress"]
            city = store["address"]["addressLocality"]
            state = store["address"]["addressRegion"]
            zc = store["address"]["postalCode"]

            phone = base.find(class_="store-contact").text.strip()
            hours = " ".join(
                list(base.find_all(class_="store-hours")[-1].stripped_strings)
            )

        add = (
            add.replace("Suite", " Suite")
            .replace("  ", " ")
            .replace("&amp;", "&")
            .replace("&Amp;", "&")
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
            store_number=store_num,
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
