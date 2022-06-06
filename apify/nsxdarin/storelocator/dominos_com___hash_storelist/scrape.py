from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time

session = SgRequests()

logger = SgLogSetup().get_logger("dominos_com___hash_storelist")


def fetch_data():
    urls = [
        "PERU|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=PE&g=1&latitude=-9.0827703&longitude=-76.19097549999998",
        "CROATIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=HR&g=1&latitude=45.8401746&longitude=15.8942922",
        "SWITZERLAND|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=CH&g=1&latitude=47.373878&longitude=8.545094",
        "GHANA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=GH&g=1&latitude=9.0324906&longitude=6.4337695",
        "MALAYSIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=MY&g=1&latitude=4.5693754&longitude=102.2656823",
        "MOROCCO|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=MA&g=1&latitude=33.589886&longitude=-7.6038690000000315",
        "NIGERIA|https://order.golo02.dominos.com/store-locator-international/locate/store?regionCode=NG&g=1&latitude=9.0324906&longitude=6.4337695",
    ]
    Found = True
    while Found:
        count = 0
        for url in urls:
            time.sleep(1)
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
                "DPZ-Market": url.split("|")[0],
            }
            r = session.get(url.split("|")[1], headers=headers)
            logger.info(url.split("|")[0])
            website = "dominos.com/#storelist"
            typ = "<MISSING>"
            country = url.split("regionCode=")[1].split("&")[0]
            loc = "<MISSING>"
            logger.info("Pulling Stores")
            for item in json.loads(r.content)["Stores"]:
                store = country + "-" + item["StoreID"]
                try:
                    name = item["StoreName"]
                except:
                    name = "<MISSING>"
                try:
                    phone = item["Phone"]
                except:
                    phone = "<MISSING>"
                state = "<MISSING>"
                try:
                    add = (
                        item["StreetName"]
                        .replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                    )
                except:
                    add = "<MISSING>"
                try:
                    zc = item["PostalCode"]
                except:
                    zc = "<MISSING>"
                try:
                    city = item["City"].replace("\r", "").replace("\n", "")
                except:
                    city = "<MISSING>"
                try:
                    hours = (
                        item["HoursDescription"]
                        .replace("\r", "")
                        .replace("\n", "")
                        .replace("\t", "")
                    )
                except:
                    hours = "<MISSING>"
                lat = item["Latitude"]
                lng = item["Longitude"]
                count = count + 1
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
        if count >= 430:
            Found = False


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
