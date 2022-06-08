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
website = "hatcreekburgers_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://hatcreekburgers.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://hatcreekburgers.com/locations"
        log.info("Fetching all the Tokens for the API...")
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp = soup.find("div", {"class": "sprig-component"})["data-hx-vals"]
        temp = json.loads(temp)
        site_id = temp["sprig:siteId"]
        template = temp["sprig:template"]
        loclist = soup.find("div", {"class": "gm-map"})["data-dna"]
        loclist = json.loads(loclist)[1:-1]
        for loc in loclist:
            temp = loc["locations"][0]
            latitude = temp["lat"]
            longitude = temp["lng"]
            res_id = temp["id"].split("-")[0]
            api_url = (
                "https://hatcreekburgers.com/index.php/actions/sprig-core/components/render?query=&sprigDistance=false&restaurantId="
                + res_id
                + "&sprig%3AsiteId="
                + site_id
                + "&sprig%3Atemplate="
                + template
            )
            r = session.get(api_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            page_url = soup.find("a")["href"]
            log.info(page_url)
            temp = soup.findAll("div", {"class": "bg-rose"})
            hours_of_operation = (
                temp[-1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Hours", "")
            )
            address = temp[-2].get_text(separator="|", strip=True).split("|")
            location_name = address[0]
            if "(" not in address[-1]:
                phone = MISSING
                address = " ".join(address[1:])
            else:
                phone = address[-1]
                address = " ".join(address[1:-1])
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
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=res_id,
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
