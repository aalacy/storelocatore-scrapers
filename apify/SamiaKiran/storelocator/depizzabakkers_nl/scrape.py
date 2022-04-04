import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "depizzabakkers_nl"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://www.depizzabakkers.nl"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        pattern = re.compile(r"\s\s+")
        url = "https://www.depizzabakkers.nl/vestigingen/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("h3")[:-2]
        for loc in loclist:
            location_name = loc.text
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                phone = soup.select_one("a[href*=tel]").text
            except:
                phone = MISSING
            loc = soup.find("div", {"id": "online_bestellen"})
            temp = loc.get_text(separator="|", strip=True).replace("|", " ")
            try:
                temp = temp.split("Openingstijden")[1]
            except:
                try:
                    temp = temp.split("OPENiNGSTijDEN")[1]
                except:
                    try:
                        temp = temp.split("ADRES")[1]
                    except:
                        temp = r.text.split("Openingstijden")[1].split("@")[0]
                        temp = (
                            BeautifulSoup(temp, "html.parser")
                            .get_text(separator="|", strip=True)
                            .replace("|", " ")
                            + "@"
                        )
            temp_var = temp.rsplit("uur", 1)
            hours_of_operation = temp_var[0].replace("restaurant", "")
            hours_of_operation = hours_of_operation + "urr"
            if "@" in hours_of_operation:
                hours_of_operation = MISSING
            hours_of_operation = re.sub(pattern, "\n", hours_of_operation).replace(
                "\n", " "
            )
            try:
                raw_address = temp_var[1].split("@")[0]
            except:
                raw_address = temp_var[0].split("@")[0]
            if "!" in raw_address:
                raw_address = raw_address.split("!")[1]
            raw_address = raw_address.split()
            raw_address = " ".join(raw_address[:-1])

            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "NL"

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
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
