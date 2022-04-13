import json
import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "tcbk_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.tcbk.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.tcbk.com/locations"
        r = session.get(url, headers=headers)
        loclist = r.text.split('"features":')[1].split("}}]};")[0] + "}}"
        loclist = loclist.split('{"type":"Feature",')[1:]
        for loc in loclist:
            loc = "{" + loc.replace("}},", "}}")
            loc = json.loads(loc)
            location_type = loc["properties"]["marker"]
            latitude = loc["geometry"]["coordinates"][-1]
            longitude = loc["geometry"]["coordinates"][0]
            loc = loc["properties"]
            hours_of_operation = loc["hours"]
            hours_of_operation = (
                BeautifulSoup(hours_of_operation, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Only Drive Up access is available until further notice.", "")
                .replace("The drive up hours will be 9:00-11:30 – Drive Up Only", "")
                .replace("2.22 miles", "")
                .replace("Hours", "")
                .replace("Lobby", "")
                .replace("This branch will be closed 2/16/22", "")
                .replace("Located inside of Raleys", "")
            )
            location_name = loc["name"]
            log.info(location_name)
            store_number = loc["id"]
            phone = loc["phone"]
            address = loc["aF"].replace("US", "").replace("<br />", " ")
            street_address = address[0]
            address = address.replace(",", " ")
            address = usaddress.parse(address)
            i = 0
            street_address = ""
            city = ""
            state = ""
            zip_postal = ""
            while i < len(address):
                temp = address[i]
                if (
                    temp[1].find("Address") != -1
                    or temp[1].find("Street") != -1
                    or temp[1].find("Recipient") != -1
                    or temp[1].find("Occupancy") != -1
                    or temp[1].find("BuildingName") != -1
                    or temp[1].find("USPSBoxType") != -1
                    or temp[1].find("USPSBoxID") != -1
                ):
                    street_address = street_address + " " + temp[0]
                if temp[1].find("PlaceName") != -1:
                    city = city + " " + temp[0]
                if temp[1].find("StateName") != -1:
                    state = state + " " + temp[0]
                if temp[1].find("ZipCode") != -1:
                    zip_postal = zip_postal + " " + temp[0]
                i += 1
            zip_postal = zip_postal.split()[0]
            state = state.split()[0]
            if "Drive" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Drive")[0]
            hours_of_operation = hours_of_operation.replace("s Mon", "Mon")
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
