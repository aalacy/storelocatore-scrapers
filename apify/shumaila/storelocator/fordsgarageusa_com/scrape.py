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

    url = "https://www.fordsgarageusa.com/locations/"
    r = session.get(url, headers=headers)
    soup1 = BeautifulSoup(r.text, "html.parser")
    divlist = soup1.findAll("div", {"class": "wpb_text_column"})

    for div in divlist:

        title = div.find("h4").text
        link = "https://www.fordsgarageusa.com" + div.find("a")["href"]

        street = div.text.strip().splitlines()[1]
        city, state = div.text.strip().splitlines()[2].split(", ", 1)
        state, pcode = state.split(" ", 1)
        phone = div.text.strip().splitlines()[3].replace("Phone: ", "")
        hours = (
            div.text.split("Phone: ", 1)[1]
            .split("\n", 1)[1]
            .split("VIEW", 1)[0]
            .replace("\n", " ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://www.fordsgarageusa.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.replace("\n", "").strip(),
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
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
