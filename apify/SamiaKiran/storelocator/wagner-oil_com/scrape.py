from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "wagner-oil_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://wagner-oil.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.wagner-oil.com/wagner-sites"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "ct-section-inner-wrap"})[2].findAll(
            "div", {"class": "ct-div-block"}
        )
        for loc in loclist:
            try:
                location_name = loc.find("h2").find("span").text
            except:
                continue
            log.info(location_name)
            temp_list = loc.findAll("p")
            try:
                latitude, longitude = (
                    temp_list[0]
                    .find("a")["href"]
                    .split("[")[3]
                    .split("]]", 1)[0]
                    .strip()
                    .split(",")
                )
            except:
                latitude = MISSING
                longitude = MISSING
            street_address = temp_list[0].find("a").text
            phone = temp_list[1].find("a").text
            address = location_name.split(",")
            city = address[0]
            state = address[1]
            url = "https://www.wagner-oil.com/wagner-sites"
            country_code = "US"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address,
                city=city.strip(),
                state=state.strip(),
                zip_postal=MISSING,
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=MISSING,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PHONE, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
