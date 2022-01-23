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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://winsteadssteakburger.com/locations-hours/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("div", {"class": "et_pb_blurb_description"}).findAll("p")
    address = city = street = pcode = state = phone = ""
    hours = ""
    for div in divlist:
        content = re.sub(cleanr, "\n", str(div))
        content = re.sub(pattern, "\n", str(content)).strip()

        if "Drive-thru" in content:
            continue
        elif "Hours" in content:
            hours = content
            hours = hours.replace("\n", " ").replace("Hours of Operation", "").strip()
            yield SgRecord(
                locator_domain="https://winsteadssteakburger.com/",
                page_url="https://winsteadssteakburger.com/",
                location_name="Winsteads Steakburger",
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=SgRecord.MISSING,
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude="<MISSING>",
                hours_of_operation=hours,
            )
            address = city = street = pcode = ""
        else:
            address = content.splitlines()
            try:
                street = address[0]
            except:
                continue
            city, state = address[1].split(", ", 1)
            state, pcode = state.split(" ", 1)
            phone = address[-1]


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS}),
            duplicate_streak_failure_factor=5,
        )
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
