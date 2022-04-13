from bs4 import BeautifulSoup
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

    url = "https://www.shoppersvaluefoodsla.com/contact-us-and-store-info/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.text.split("Locations", 1)[1].split("Shoppers Value Foods")[2:]

    for loc in loclist:
        loc = loc.split("Store Manager", 1)[0].strip()
        hours = loc.split("Hours:", 1)[1].replace("\n", " ").strip()
        loc = loc.splitlines()
        street = loc[0]
        city, state = loc[1].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = loc[2].replace("Phone: ", "")

        yield SgRecord(
            locator_domain="https://www.shoppersvaluefoodsla.com/",
            page_url=url,
            location_name="Shoppers Value Foods",
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


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
