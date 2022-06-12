from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser


session = SgRequests()
website = "wefloridafinancial_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "authority": "www.wefloridafinancial.com",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
}

DOMAIN = "https://www.wefloridafinancial.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.wefloridafinancial.com/belong/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.findAll("a", {"class": "sppb-btn sppb-btn-link"})
        for link in div:
            page_url = "https://www.wefloridafinancial.com" + link["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            bs = BeautifulSoup(r.text, "html.parser")
            title = bs.find("h1", {"class": "sppb-addon-title"}).text
            temp = bs.find("h5").find("a")["href"]
            address = temp.split("/place/")[1].split("/@")[0].replace("+", " ").strip()
            lat, lng = temp.split("/@")[1].split(",1")[0].split(",")
            hours = (
                bs.find("table").get_text(separator="|", strip=True).replace("|", " ")
            )
            hours = hours.replace("LOBBY HOURS ", "")
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
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code="US",
                store_number=MISSING,
                phone=MISSING,
                location_type=MISSING,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours.strip(),
                raw_address=address.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
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
