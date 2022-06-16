import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "rax_fi"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.rax.fi"
MISSING = SgRecord.MISSING


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    if True:
        url = "https://www.rax.fi/ravintolat"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "MuiGrid-root"})[4].findAll("a")
        for loc in loclist:
            page_url = DOMAIN + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            schema = r.text.split(
                '<script data-react-helmet="true" type="application/ld+json">'
            )[2].split("</script>", 1)[0]
            schema = schema.replace("\n", "")
            loc = json.loads(schema)
            location_name = strip_accents(loc["name"])
            phone = soup.select_one("a[href*=tel]").text
            address = loc["address"]
            street_address = strip_accents(address["streetAddress"])
            city = strip_accents(address["addressLocality"])
            state = MISSING
            zip_postal = address["postalCode"]
            country_code = "FI"
            hour_list = loc["openingHoursSpecification"]
            hours_of_operation = ""
            for hour in hour_list:
                day = hour["dayOfWeek"].replace("http://schema.org/", "")
                time = hour["opens"] + "-" + hour["closes"]
                hours_of_operation = hours_of_operation + " " + day + " " + time
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation,
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
