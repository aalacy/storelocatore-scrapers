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
    url = "https://prostheticsolutions.com/contact/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("div", {"class": "wp-block-column"})
    flag = 0
    for loc in loclist:
        loc = re.sub(cleanr, "\n", str(loc)).strip()
        loc = re.sub(pattern, "\n", str(loc)).strip().splitlines()
        title = loc[0]
        street = loc[1]
        city, state = loc[2].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = loc[4]

        if flag == 0:
            lat = r.text.split('"latitude":"', 1)[1].split('"', 1)[0]
            longt = r.text.split('"longitude":"', 1)[1].split('"', 1)[0]
            flag = 1
        else:
            lat = longt = "<MISSING>"
        yield SgRecord(
            locator_domain="https://prostheticsolutions.com/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
