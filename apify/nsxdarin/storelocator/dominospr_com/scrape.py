from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog
import json

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "DPZ-Market": "PUERTO_RICO",
}

logger = SgLogSetup().get_logger("dominospr_com")


def fetch_data():
    cityurl = "https://order.golo01.dominos.com/store-locator-international/locations/neighborhood?regionCode=PR"
    r = session.get(cityurl, headers=headers)
    districts = []
    for item in json.loads(r.content):
        if item["city"] not in districts:
            districts.append(item["city"])
    for dist in districts:
        logger.info(dist)
        try:
            lurl = (
                "https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=PR&type=Carryout&LocationName=&Name=&Street=&StreetName=&StreetNumber=&UnitNumber=&City="
                + dist
                + "&Neighborhood=&Region=PR&PostalCode=&DeliveryInstructions=&Type=House&IsDefault=false&PlaceName=&OrganizationName=&streetAddress1=&PlaceType=&AddressType=House&UnitType=House&g=1"
            )
            r = session.get(lurl, headers=headers)
            website = "dominospr.com"
            typ = "<MISSING>"
            country = lurl.split("regionCode=")[1].split("&")[0]
            loc = "<MISSING>"
            store = "<MISSING>"
            hours = "<MISSING>"
            lat = "<MISSING>"
            lng = "<MISSING>"
            for item in json.loads(r.content)["Stores"]:
                if "StoreName" in str(item):
                    name = item["StoreName"]
                    store = item["StoreID"]
                    phone = item["Phone"]
                    try:
                        add = item["StreetName"]
                    except:
                        add = "<MISSING>"
                    add = str(add).replace("\r", "").replace("\n", "")
                    city = str(item["City"]).replace("\r", "").replace("\n", "")
                    state = "<MISSING>"
                    zc = item["PostalCode"]
                    try:
                        lat = item["StoreCoordinates"]["StoreLatitude"]
                        lng = item["StoreCoordinates"]["StoreLongitude"]
                    except:
                        lat = "<MISSING>"
                        lng = "<MISSING>"
                    hours = (
                        str(item["HoursDescription"])
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("\r", "")
                    )
                    loc = "<MISSING>"
                    if zc == "USA" or "PR" in zc:
                        zc = "<MISSING>"
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
