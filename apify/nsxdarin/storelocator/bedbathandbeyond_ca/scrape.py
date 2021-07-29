from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("bedbathandbeyond_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    urls = [
        "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%22Winnipeg%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+or+%5C%22country%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2250%22,%22CA%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%224000%22,%22maxMatches%22:500,%22ambiguities%22:%22ignore%22,%22units%22:%22k%22%7D%7D&__amp_source_origin=https%3A%2F%2Fwww.bedbathandbeyond.ca",
        "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%22Ottawa%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+or+%5C%22country%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2250%22,%22CA%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%224000%22,%22maxMatches%22:500,%22ambiguities%22:%22ignore%22,%22units%22:%22k%22%7D%7D&__amp_source_origin=https%3A%2F%2Fwww.bedbathandbeyond.ca",
        "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%22Vancouver%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+or+%5C%22country%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2250%22,%22CA%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%224000%22,%22maxMatches%22:500,%22ambiguities%22:%22ignore%22,%22units%22:%22k%22%7D%7D&__amp_source_origin=https%3A%2F%2Fwww.bedbathandbeyond.ca",
        "https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Clu6120u8nh,2w%3Do5-lwt2l&inFormat=json&json=%7B%22origin%22:%22Montreal%22,%22hostedDataList%22:[%7B%22extraCriteria%22:%22(+%5C%22display_online%5C%22+%3D+%3F+)+and+(+%5C%22store_type%5C%22+%3D+%3F+or+%5C%22country%5C%22+%3D+%3F+)%22,%22tableName%22:%22mqap.34703_AllInfo%22,%22parameters%22:[%22Y%22,%2250%22,%22CA%22],%22columnNames%22:[]%7D],%22options%22:%7B%22radius%22:%224000%22,%22maxMatches%22:500,%22ambiguities%22:%22ignore%22,%22units%22:%22k%22%7D%7D&__amp_source_origin=https%3A%2F%2Fwww.bedbathandbeyond.ca",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        for item in json.loads(r.content)["searchResults"]:
            website = "bedbathandbeyond.ca"
            typ = "<MISSING>"
            name = item["name"]
            state = item["fields"]["state"]
            add = item["fields"]["address"]
            country = "CA"
            zc = item["fields"]["postal"]
            city = item["fields"]["city"]
            lng = item["fields"]["Lng"]
            lat = item["fields"]["Lat"]
            phone = item["fields"]["Phone"]
            loc = "<MISSING>"
            store = item["fields"]["RecordId"]
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
