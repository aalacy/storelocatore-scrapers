import json
import usaddress
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "towncaredental_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.towncaredental.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.towncaredental.com/locations"
        r = session.get(url, headers=headers)
        loclist = (
            r.text.split("window.app_data = JSON.parse('")[1]
            .replace("\\u0022", '"')
            .split('"stores":[{')[1]
            .split(',"userLocation"')[0]
        )
        loclist = json.loads("[{" + loclist)
        for loc in loclist:
            page_url = loc["uri"].replace("\\/", "/")
            log.info(page_url)
            temp_url = page_url + "/about-our-practice"
            r = session.get(temp_url, headers=headers)
            hour_list = r.text.split('"openingHoursSpecification":[{')[1].split("]}")[0]
            hour_list = json.loads("[{" + hour_list + "]")
            hours_of_operation = ""
            for hour in hour_list:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hour["dayOfWeek"]
                    + " "
                    + hour["opens"]
                    + "-"
                    + hour["closes"]
                )
            location_name = loc["name"].replace("G\\u0026G", "G&G")
            store_number = loc["id"]
            phone = loc["phone_number"]
            address = " ".join(loc["addressLines"])
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
            country_code = "US"
            latitude = loc["position"]["lat"]
            longitude = loc["position"]["lng"]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=MISSING,
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
