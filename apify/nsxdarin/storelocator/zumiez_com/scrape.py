from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("zumiez_com")


def fetch_data():
    logger.info("Pulling Stores...")
    url = "https://www.zumiez.com/storelocator/search/latlng/?lat=40.7135097&lng=-73.9859414&radius=10000"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item["locator_id"]
        website = "zumiez.com"
        typ = "Store"
        loc = "https://www.zumiez.com/storelocator/store/index/id/" + store
        hours = ""
        country = "US"
        name = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split(" |")[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
            if 'itemprop="addressLocality">' in line2:
                city = (
                    line2.split('itemprop="addressLocality">')[1]
                    .split("<")[0]
                    .replace(",", "")
                )
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0]
            if 'itemprop="latitude">' in line2:
                lat = line2.split('content="')[1].split('"')[0]
            if 'itemprop="longitude">' in line2:
                lng = line2.split('content="')[1].split('"')[0]
            if 'itemprop="openingHours" datetime="' in line2:
                hrs = (
                    line2.split('itemprop="openingHours" datetime="')[1]
                    .split('"')[0]
                    .replace("&nbsp;", " ")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
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
