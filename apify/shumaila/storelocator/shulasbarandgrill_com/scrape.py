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

    url = "https://shulassteakhouse.com/#locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "shula-menu__location"})

    for div in divlist:
        if "shulasbarandgrill" in div.find("a")["href"]:
            pass
        else:
            continue
        link = div.find("a")["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        titlelist = soup.findAll("div", {"class": "location"})
        addresslist = soup.findAll("div", {"class": "location-info"})

        for i in range(0, len(titlelist)):
            title = titlelist[i].text
            address = addresslist[i].text.splitlines()
            city, state = address[-1].split(", ")
            state, pcode = state.lstrip().split(" ", 1)

            street = address[-2]

            yield SgRecord(
                locator_domain="https://shulasbarandgrill.com/",
                page_url=link,
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
                longitude=SgRecord.MISSING,
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
