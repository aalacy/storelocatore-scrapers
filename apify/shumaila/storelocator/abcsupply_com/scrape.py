import usaddress
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "abcsupply_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://abcsupply.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]

    for i in range(0, len(states)):
        url = "https://www.abcsupply.com/locations/location-results"
        result = session.post(url, data={"State": states[i]}, headers=headers)
        soup = BeautifulSoup(result.text, "html.parser")
        divlist = soup.findAll("div", {"class": "location"})
        maplist = result.text.split("var marker = new google.maps.Marker({")[1:]
        for div in divlist:
            location_name = (
                div.find("div", {"class": "location-name"})
                .text.replace("\n", " ")
                .strip()
            )
            store_number = (
                div.find("div", {"class": "location-name"})
                .find("a")["id"]
                .split("_", 1)[1]
            )
            page_url = (
                "https://www.abcsupply.com"
                + div.find("div", {"class": "location-name"}).find("a")["href"]
            )
            log.info(page_url)
            address = (
                div.find("div", {"class": "location-address"})
                .get_text(separator="|", strip=True)
                .split("|")
            )
            phone = div.select_one("a[href*=tel]").text
            raw_address = " ".join(address)
            address = raw_address.replace(",", " ").replace(phone, "")
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
            try:
                hours_of_operation = (
                    div.find("div", {"class": "hours-detail"})
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                hours_of_operation = MISSING
            latitude = longitude = MISSING
            for coord in maplist:
                coord = coord.split(");", 1)[0]
                if location_name + " - ABC Supply #" + store_number in coord:
                    latitude = coord.split("lat: ", 1)[1].split(",", 1)[0]
                    longitude = coord.split("lng: ", 1)[1].split(" }", 1)[0]
                    break
            if len(phone) < 3:
                phone = MISSING
            if len(latitude) < 3:
                latitude = MISSING
            if len(longitude) < 3:
                longitude = MISSING
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
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
