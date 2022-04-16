import json
import usaddress
from lxml import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "bhotelsandresorts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://bhotelsandresorts.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    r = session.get("https://www.bhotelsandresorts.com/destinations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script_temp = soup.find(id="menu-main").ul
    for script_location in script_temp.find_all("li"):
        page_url = script_location.find("a")["href"]
        log.info(page_url)
        r1 = session.get(page_url, headers=headers)
        tree = html.fromstring(r1.text)
        text = "".join(tree.xpath("//script[contains(text(), 'places')]/text()"))
        text = text.split('"places":[')[-1].split("}}")[0] + "}}}"
        try:
            address_json = json.loads(text)
            got_page = True
        except:
            got_page = False
        if got_page:
            location_name = address_json["title"]
            store_number = address_json["id"]
            latitude = address_json["location"]["lat"]
            longitude = address_json["location"]["lng"]
            try:
                phone = address_json["content"]
            except:
                phone = MISSING
            if "Directions" in phone:
                phone = MISSING
            address = address_json["address"]
            address = address.replace(",", " ").replace("USA", "")
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
            if not zip_postal:
                zip_postal = r1.text.split('"postal_code":"')[1].split('"')[0]
        else:
            base = BeautifulSoup(r1.text, "lxml")
            raw_data = list(
                base.find("h3", string="Contact").find_previous("div").stripped_strings
            )[1:]
            location_name = raw_data[0]
            street_address = raw_data[1]
            city_line = raw_data[2].strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_postal = city_line[-1].strip().split()[1].strip()
            phone = raw_data[4]
            store_number = ""
            latitude = ""
            longitude = ""
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
            phone=phone,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=MISSING,
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
