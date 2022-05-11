from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser
import re


session = SgRequests()
website = "giantfitnessclubs_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://giantfitnessclubs.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://giantfitnessclubs.com/locations/"
    stores_req = session.get(url, headers=headers)
    soup = BeautifulSoup(stores_req.text, "html.parser")
    locations = soup.findAll("div", {"class": "column_attr clearfix align_center"})
    for loc in locations:
        link = loc.find("a")["href"].strip()
        stores_req = session.get(link, headers=headers)
        soup = BeautifulSoup(stores_req.text, "html.parser")
        title = soup.find("h1", {"class": "title"}).text
        if title == "Jersey Girls – Women Only":
            street = MISSING
            city = MISSING
            state = MISSING
            pcode = MISSING
            phone = MISSING
            hours = MISSING
            lat = MISSING
            lng = MISSING
        else:
            info = soup.findAll("div", {"class": "column_attr clearfix"})
            address = info[0]
            if title == "Jersey Girls – Women Only – Voorhees NJ":
                address = address.text
                address = address.split("\n")[0]
                phone = info[0].text
                phone = phone.lstrip(address)
                hours = info[0].text
                hours = hours.split(phone)[1]
            if title == "Giant Fitness – Voorhees NJ":
                info = info[1].text
                address = info.split("Phone:  ")[0]
                phone = info.split("Phone:  ")[1].split("\n")[0]
                hours = info.split("Gym Hours:")[1]
            if title == "Giant Fitness – Philadelphia PA":
                address = info[1].text
                phone = info[2].text
                hours = info[3].text
            if title == "Giant Fitness – Mt Laurel NJ":
                address = info[1].find("b").text
                phone = info[2].text
                hours = info[3].text
            if title == "Giant Fitness – Mount Ephraim NJ":
                address = info[-3].text
                phone = info[-2].text
                hours = info[-1].text
            if title == "Giant Fitness – Woodbury Heights NJ":
                address = info[1].text
                phone = info[2].text
                hours = info[3].text
            if title == "Giant Fitness – Washington Township NJ":
                address = info[2].text
                phone = info[3].text
                hours = info[4].text
            if title == "Giant Fitness – Blackwood NJ":
                address = info[2].text
                phone = info[3].text
                hours = info[4].text
            address = address.strip()
            address = address.lstrip("Address:").strip()

            phone = phone.split("\n")[0]
            phone = phone.lstrip("Phone: ").strip()
            if phone == "":
                phone = MISSING

            hours = hours.replace("\n", " ").strip()
            hours = re.sub(pattern, " ", hours)
            hours = re.sub(cleanr, " ", hours)
            hours = hours.lstrip("Hours: ")

            parsed = parser.parse_address_usa(address)
            street1 = (
                parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
            )
            street = (
                (street1 + ", " + parsed.street_address_2)
                if parsed.street_address_2
                else street1
            )
            city = parsed.city if parsed.city else "<MISSING>"
            state = parsed.state if parsed.state else "<MISSING>"
            pcode = parsed.postcode if parsed.postcode else "<MISSING>"

            btn = soup.findAll("div", {"class": "button_align align_center"})[1].find(
                "a"
            )

            btn = btn["href"]
            if btn.find("/@") != -1:
                coords = btn.split("/@")[1].split(",1")[0]
                lat, lng = coords.split(",")
            else:
                lat = MISSING
                lng = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID(
            {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.HOURS_OF_OPERATION}
        )
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
