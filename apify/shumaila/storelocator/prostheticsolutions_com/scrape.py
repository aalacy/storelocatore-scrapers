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
    url = "https://prostheticsolutions.com/contact/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    titlelist = soup.find("main").findAll("h2")
    coordlist = soup.findAll("iframe")[1:]
    loc = soup.find("main").find("div", {"class": "ocb-column-inner"})
    loc = re.sub(cleanr, "\n", str(loc)).strip()
    loc = re.sub(pattern, "\n", str(loc)).strip()
    for i in range(0, len(titlelist)):
        title = titlelist[i].text
        content = loc.split(title, 1)[1].split("Fax", 1)[0].strip().splitlines()
        street = content[0]
        city, state = content[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = content[-1]
        longt, lat = (
            coordlist[i]["src"].split("!2d", 1)[1].split("!2m", 1)[0].split("!3d")
        )

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
            latitude=lat,
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
