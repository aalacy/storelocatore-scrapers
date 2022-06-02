from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("savealot_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    for x in range(40, 100):
        for y in range(-250, -120):
            midlat = str(x / 2)
            midlng = str(y / 2)
            lowlat = str(int(x) / 2 - 1)
            lowlng = str(int(y) / 2 - 1)
            hilat = str(int(x) / 2 + 1)
            hilng = str(int(y) / 2 + 1)
            url = (
                "https://savealot.com/wp-json/locator/v1/search/"
                + midlat
                + "/"
                + midlng
                + "/"
                + lowlat
                + "/"
                + lowlng
                + "/"
                + hilat
                + "/"
                + hilng
            )
            logger.info(url)
            r = session.get(url, headers=headers)
            array = json.loads(r.content)
            for item in array:
                website = "savealot.com"
                phone = item["primary_phone"]
                state = item["state"]
                store = item["store"]
                zc = item["postal_code"]
                city = item["city"]
                purl = (
                    "https://savealot.com/grocery-stores/"
                    + city.replace(" ", "-").replace(".", "")
                    + "-"
                    + zc
                    + "-"
                    + store
                )
                purl = purl.lower()
                name = "Save A Lot"
                add = item["street"]
                country = "US"
                typ = "Store"
                lat = item["lat"]
                lng = item["lng"]
                hours = ""
                try:
                    r2 = session.get(purl, headers=headers)
                    for line2 in r2.iter_lines():
                        if 'class="day">' in line2:
                            day = line2.split('class="day">')[1].split("<")[0]
                        if '<span class="hours">' in line2:
                            hrs = (
                                day
                                + ": "
                                + line2.split('<span class="hours">')[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                except:
                    pass
                if hours == "":
                    hours = "<MISSING>"
                yield SgRecord(
                    locator_domain=website,
                    page_url=purl,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
