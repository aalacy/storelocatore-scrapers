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
    url = "https://bikerbarre.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    location_data = soup.find_all("div", {"class": "col-md-3 locations"})[0].find_all(
        "div"
    )

    for store in location_data:
        store_name = store.p.text.split("\n")[0]
        street_add = re.findall("\t\t\t\t\t\t\t\t(.*)<br/>\n\t", str(store))[0]
        city = re.findall("<br/>\n\t\t\t\t\t\t\t\t(.*), ", str(store))[0]
        state = re.findall(", ([A-Za-z]{2}) ", str(store))[0]
        zip = re.findall(", [A-Za-z]{2} (\\d{4,5})", str(store))[0]
        phone = "<MISSING>"

        yield SgRecord(
            locator_domain=url,
            page_url="<MISSING>",
            location_name=store_name,
            street_address=street_add,
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation="<INACCESSIBLE>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
