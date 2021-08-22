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
website = "mydentalvisioncare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://kidsdentalvisioncare.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://mydentalvisioncare.com/locate-practice"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find(
            "div", {"class": "view-content locations-list loc-list"}
        ).findAll("div", {"class": "views-row"})
        for loc in loclist:
            page_url = loc.find("a")["href"]
            store_number = page_url.split("/")[-1]
            r = session.get(page_url, headers=headers, allow_redirects=True)
            page_url = r.url
            log.info(page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            if "currently CLOSED" in r.text:
                continue
            location_name = soup.find(
                "span", {"class": "block text-mdvcblue-500 xl:inline"}
            ).text
            address = soup.find("span", {"class": "block w-40 sm:w-full"}).text
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
            phone = soup.find(
                "a", {"class": "text-mdvcblue-500 hover:text-mdvcblue-900"}
            ).text
            location_type = MISSING
            coords = json.loads(soup.find("div", {"class": "gm-map"})["data-dna"])
            for coord in coords:
                try:
                    coord_temp = coord["options"]["infoWindowOptions"]["content"]
                except:
                    continue
                coord_temp = BeautifulSoup(coord_temp, "html.parser")
                if zip_postal in coord_temp.text:
                    coord = coord["locations"]
                    latitude = str(coord).split("'lat': ")[1].split(",")[0]
                    longitude = str(coord).split("'lng': ")[1].split(",")[0]
                    break
            hours_of_operation = soup.find("div", {"class": "max-w-lg px-4"}).findAll(
                "li"
            )
            hours_of_operation = " ".join(
                x.find("p")
                .text.strip()
                .replace("\n", "")
                .replace("-                      ", "- ")
                for x in hours_of_operation
            )
            country_code = "US"
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
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
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
