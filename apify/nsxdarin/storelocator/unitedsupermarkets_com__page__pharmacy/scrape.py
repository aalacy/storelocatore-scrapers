from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("unitedsupermarkets_com__page__pharmacy")


def fetch_data():
    url = "https://www.unitedsupermarkets.com/rs/store-locator"
    r = session.get(url, headers=headers)
    token = ""
    for line in r.iter_lines():
        if "var antiForgeryToken = '" in line:
            token = line.split("var antiForgeryToken = '")[1].split("'")[0]
    url = "https://www.unitedsupermarkets.com/RS.Relationshop/StoreLocation/GetAllStoresPosition"
    payload = {"__RequestVerificationToken": token}
    r = session.post(url, headers=headers, data=payload)
    website = "unitedsupermarkets.com/page/pharmacy"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"Active":' in line:
            items = line.split('{"Active":')
            for item in items:
                if '"Address1":"' in item:
                    Pharm = False
                    name = item.split('"StoreName":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    add = item.split('"Address1":"')[1].split('"')[0]
                    store = item.split('"StoreID":')[1].split(",")[0]
                    loc = (
                        "https://www.unitedsupermarkets.com/rs/StoreLocator?id=" + store
                    )
                    state = item.split('"State":"')[1].split('"')[0]
                    zc = item.split('"Zipcode":"')[1].split('"')[0]
                    phone = ""
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    hours = ""
                    PFound = False
                    r2 = session.get(loc, headers=headers)
                    time.sleep(15)
                    for line2 in r2.iter_lines():
                        if '<h2 class="sub-title">Pharmacy</h2>' in line2:
                            Pharm = True
                        if Pharm and '<div class="store-hours-detail">' in line2:
                            PFound = True
                        if PFound and "</div>" in line2:
                            PFound = False
                        if Pharm and "<span>Phone:" in line2 and phone == "":
                            phone = line2.split("<span>Phone:")[1].split("<")[0].strip()
                        if PFound and "day:" in line2 and "<span>" in line2:
                            hrs = line2.split("<span>")[1].split("<")[0].strip()
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if hours == "":
                        hours = "<MISSING>"
                    if phone == "":
                        phone = "<MISSING>"
                    if Pharm:
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
