from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "practical_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.practical.co.uk/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.practical.co.uk/locator.asp"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("select", {"name": "franchiseLoc"}).findAll("option")
        for loc in loclist[1:]:
            page_url = DOMAIN + loc["value"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("span", {"itemprop": "name"}).text
            street_address = (
                soup.find("span", {"itemprop": "streetAddress"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace(".", "")
            )
            city = (
                soup.find("span", {"itemprop": "addressLocality"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
                .replace(".", "")
            )
            state = (
                soup.find("span", {"itemprop": "addressRegion"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
                .replace(".", "")
            )
            zip_postal = soup.find("span", {"itemprop": "postalCode"}).text.replace(
                ".", ""
            )
            raw_address = street_address + " " + city + " " + state + " " + zip_postal
            pa = parse_address_intl(street_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            country_code = (
                soup.find("span", {"itemprop": "addressCountry"})
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            phone = soup.find("span", {"itemprop": "telephone"}).text
            latitude = soup.find("span", {"class": "latitude"}).find("span")["title"]
            longitude = soup.find("span", {"class": "longitude"}).find("span")["title"]
            hours_of_operation = (
                soup.find("td", {"id": "contact"})
                .get_text(separator="|", strip=True)
                .split("|")[-1]
                .lower()
                .replace("& B/Hols", "")
                .replace("fri0", "fri")
                .replace("16.30losed", "16.30 closed")
                .replace("(last collection 30 mins before closing) ", "")
                .replace("Delivery & Collection Service", "")
                .replace("now open..... ", "")
            )
            if "out of hours" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("out of hours")[0]
            elif "last collection" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("last collection")[0]
            elif "emergency" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("emergency")[0]
            if "mon" not in hours_of_operation:
                if "weekdays" not in hours_of_operation:
                    hours_of_operation = MISSING
            hours_of_operation = hours_of_operation.strip("-").strip(",")
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.RAW_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
