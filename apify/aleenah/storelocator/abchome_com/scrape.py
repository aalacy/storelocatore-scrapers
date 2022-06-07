from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    pattern = re.compile(r"\s\s+")
    cleanr = re.compile(r"<[^>]+>")
    url = "https://abchome.com/pages/contact"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location__intro"})
    for div in divlist:
        title = div.find("h2").text.strip()
        address = str(div.find("div", {"class": "location__store-address"}))
        address = re.sub(cleanr, "\n", address)
        address = re.sub(pattern, "\n", address).strip().splitlines()
        street = address[1]
        city, state = address[2].split(", ", 1)
        state, pcode = state.split(" ", 1)
        state = state.replace(",", "").strip()
        hours = (
            div.find("div", {"class": "location__store-hours"})
            .text.strip()
            .replace("Hours", "")
            .replace("\n", " ")
            .replace("pm", "pm ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://abchome.com/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation=hours,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
