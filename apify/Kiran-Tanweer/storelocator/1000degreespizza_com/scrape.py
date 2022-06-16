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

    url = "https://www.1000degreespizza.com/pizza-place-near-me-locations/#toggle-id-2"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "location-1000d"})
    for div in divlist:

        try:
            link = div.findAll("a")[-1]["href"]
            if "../" in link:
                link = link.replace("../", "https://www.1000degreespizza.com/")
        except:
            continue
        if "NOW OPEN!" in div.text:
            div = div.text.split("NOW OPEN!", 1)[0].strip().splitlines()
        else:
            div = div.text.strip().splitlines()
        m = 0

        title = div[m]
        m = m + 1
        street = div[m]
        m = m + 1
        if len(div) == 5:
            street = street + " " + div[m]
            m = m + 1
        city, state = div[m].split(", ", 1)
        phone = div[-1]

        yield SgRecord(
            locator_domain="https://www.1000degreespizza.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=SgRecord.MISSING,
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude="<MISSING>",
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
