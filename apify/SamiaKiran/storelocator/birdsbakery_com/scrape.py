from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "birdsbakery_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://birdsbakery.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://birdsbakery.com/stores.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "store-listings"}).findAll("li")
        for loc in loclist:
            hours = loc.find("div")["data-opening-hours"].split("|")
            mo = "Mon " + hours[0]
            tu = " Tue " + hours[1]
            we = " Wed " + hours[2]
            th = " Thu " + hours[3]
            fr = " Fri " + hours[4]
            sa = " Sat " + hours[5]
            su = " Sat " + hours[6]
            hours_of_operation = mo + tu + we + th + fr + sa + su
            location_name = loc.find("h3").text
            log.info(location_name)
            address = loc.find("address").findAll("p")
            phone = address[-1].text.replace("Tel:", "")
            address = address[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            city = address[1]
            state = MISSING
            zip_postal = address[2]
            country_code = "UK"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
