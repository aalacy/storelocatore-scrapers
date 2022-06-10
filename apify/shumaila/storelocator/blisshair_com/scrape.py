from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.blisshair.com/the-best-hair-salons-in-nottingham-loughborough/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "so-widget-sow-editor-base"})
    for div in divlist:
        try:
            title = div.find("h3").text.strip()
        except:
            continue
        address = div.findAll("p")[0].text.splitlines()
        street = address[0]
        try:
            city, state = address[1].split(", ", 1)
        except:
            city = address[1]
            if "Loughorough" in city:
                state = "Leicestershire"
        pcode = address[2]
        phone = div.findAll("p")[1].text

        yield SgRecord(
            locator_domain="https://www.blisshair.com/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="GB",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation="<MISSING>",
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
