import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "spar_pt"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://spar.pt/"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.spar.pt/rede-de-lojas"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.find(
            "div", {"class": "vc_single_image-wrapper vc_box_border_grey"}
        ).findAll("tbody")
        for idx, link in enumerate(linklist):
            loclist = link.find("tr")
            loclist = str(loclist).split("<tr>")[1:]
            for loc in loclist:
                loc = BeautifulSoup(loc, "html.parser")
                loc = loc.get_text(separator="|", strip=True).split("|")
                if idx == 1:
                    location_type = "Franchise store"
                else:
                    location_type = "Own store"
                location_name = strip_accents(loc[0])
                if "**" in location_name:
                    location_type = "Temporarily Closed"
                location_name = location_name.replace("*", "")
                if not location_name:
                    continue
                log.info(location_name)
                street_address = strip_accents(loc[1])
                if location_type == "Franchise store":
                    city = strip_accents(loc[-1])
                    phone = MISSING
                    zip_postal = loc[-2]
                else:
                    city = strip_accents(loc[2])
                    phone = loc[-1]
                    zip_postal = loc[-2]
                state = MISSING
                country_code = "PT"
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
                    phone=phone,
                    location_type=location_type,
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=MISSING,
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
