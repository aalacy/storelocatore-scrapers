from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("bedbathandbeyond_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    urls = [
        "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh%2C2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22%3A%2255441%22%2C%22hostedDataList%22%3A%5B%7B%22extraCriteria%22%3A%22(%20%5C%22display_online%5C%22%20%3D%20%3F%20)%20and%20(%20%5C%22store_type%5C%22%20%3D%20%3F%20)%22%2C%22tableName%22%3A%22mqap.34703_AllInfo%22%2C%22parameters%22%3A%5B%22Y%22%2C%2210%22%5D%2C%22columnNames%22%3A%5B%5D%7D%5D%2C%22options%22%3A%7B%22radius%22%3A2500%2C%22ambiguities%22%3A%22ignore%22%2C%22maxMatches%22%3A2000%2C%22units%22%3A%22m%22%7D%7D",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)["searchResults"]:
            website = "bedbathandbeyond.com"
            typ = "<MISSING>"
            name = item["name"]
            state = item["fields"]["state"]
            add = item["fields"]["address"]
            country = "US"
            zc = item["fields"]["postal"]
            city = item["fields"]["city"]
            lng = item["fields"]["Lng"]
            lat = item["fields"]["Lat"]
            phone = item["fields"]["Phone"]
            store = item["fields"]["RecordId"]
            loc = "https://www.bedbathandbeyond.com/store/pickup/store-" + store
            hours = (
                "Sun: "
                + str(item["fields"]["SUN_OPEN"])
                + "-"
                + str(item["fields"]["SUN_CLOSE"])
            )
            hours = (
                hours
                + "; Mon: "
                + str(item["fields"]["MON_OPEN"])
                + "-"
                + str(item["fields"]["MON_CLOSE"])
            )
            hours = (
                hours
                + "; Tue: "
                + str(item["fields"]["TUES_OPEN"])
                + "-"
                + str(item["fields"]["TUES_CLOSE"])
            )
            hours = (
                hours
                + "; Wed: "
                + str(item["fields"]["WED_OPEN"])
                + "-"
                + str(item["fields"]["WED_CLOSE"])
            )
            hours = (
                hours
                + "; Thu: "
                + str(item["fields"]["THURS_OPEN"])
                + "-"
                + str(item["fields"]["THURS_CLOSE"])
            )
            hours = (
                hours
                + "; Fri: "
                + str(item["fields"]["FRI_OPEN"])
                + "-"
                + str(item["fields"]["FRI_CLOSE"])
            )
            hours = (
                hours
                + "; Sat: "
                + str(item["fields"]["SAT_OPEN"])
                + "-"
                + str(item["fields"]["SAT_CLOSE"])
            )
            hours = hours.replace(": 0-0;", ": Closed")
            hours = hours.replace("Sat: 0-0", "Sat: Closed")
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
