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
    ids = []
    for x in range(20, 70):
        for y in range(-130, -65):
            logger.info("%s - %s..." % (str(x), str(y)))
            midlat = str(x)
            midlng = str(y)
            lowlat = str(int(x) - 1)
            lowlng = str(int(y) - 1)
            hilat = str(int(x) + 1)
            hilng = str(int(y) + 1)
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
            r = session.get(url, headers=headers, verify=False)
            array = json.loads(r.content)
            for item in array:
                website = "savealot.com"
                phone = item["primary_phone"]
                state = item["state"]
                store = item["reseller_location_id"]
                zc = item["postal_code"]
                city = item["city"]
                purl = (
                    "https://savealot.com/grocery-stores/"
                    + city.replace(" ", "-")
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
                if store not in ids:
                    ids.append(store)
                    r2 = session.get(purl, headers=headers)
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode("utf-8"))
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
