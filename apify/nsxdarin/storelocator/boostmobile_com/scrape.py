from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries, Grain_8
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
}

logger = SgLogSetup().get_logger("boostmobile_com")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_results=None,
    granularity=Grain_8(),
)


def fetch_data():

    all_zips = []

    logger.info("Appending zip_codes ..")
    for coord in search:
        if len(coord) == 4:
            coord = "0" + coord
        all_zips.append(coord)

    logger.info("Searching zip_codes .. ")
    for coord in all_zips:
        url = (
            "https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode="
            + coord
            + "&page=1"
        )
        r = session.get(url, headers=headers)
        try:
            array = json.loads(r.content, strict=False)
        except Exception:
            raise Exception(f"Err on this zip:{url}")
        count = int(array["nearestOutletResponse"]["resultsFoundNum"])
        pages = int((count - 1) / 50) + 2
        for x in range(1, pages):
            url = (
                "https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode="
                + coord
                + "&page="
                + str(x)
            )
            if str(x) != "1":
                r = session.get(url, headers=headers)
                try:
                    array = json.loads(r.content, strict=False)
                except Exception:
                    raise Exception(f"Err on this zip:{url}")
            for item in array["nearestOutletResponse"]["nearestlocationinfolist"][
                "nearestLocationInfo"
            ]:
                website = "boostmobile.com"
                store = item["id"]
                name = item["storeName"]
                typ = ""
                add = item["storeAddress"]["primaryAddressLine"]
                city = item["storeAddress"]["city"]
                state = item["storeAddress"]["state"]
                zc = item["storeAddress"]["zipCode"]
                lat = item["storeAddress"]["lat"]
                lng = item["storeAddress"]["long"]
                if lat == 30425794:
                    lat = 30.425794
                country = "US"
                phone = item["storePhone"]
                loc = item["elevateURL"]
                hours = "Mon: " + item["storeHours"]["mon"]
                hours = hours + "; Tue: " + item["storeHours"]["tue"]
                hours = hours + "; Wed: " + item["storeHours"]["wed"]
                hours = hours + "; Thu: " + item["storeHours"]["thu"]
                hours = hours + "; Fri: " + item["storeHours"]["fri"]
                hours = hours + "; Sat: " + item["storeHours"]["sat"]
                hours = hours + "; Sun: " + item["storeHours"]["sun"]
                if lat == "":
                    lat = "<MISSING>"
                if lng == "":
                    lng = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                if "see store" in hours.lower():
                    hours = "<MISSING>"
                if loc == "" or loc is None:
                    loc = "<MISSING>"
                if store != "":
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
