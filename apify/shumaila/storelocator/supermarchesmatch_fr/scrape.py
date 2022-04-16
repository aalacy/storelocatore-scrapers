from bs4 import BeautifulSoup
import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


MISSING = SgRecord.MISSING


def fetch_data():

    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.supermarchesmatch.fr/search-magasin.php?all=1"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.find_all("div", {"class": "mgsbloc"})
    for loc in loclist:
        title = loc.find("h3").text
        link = loc["onclick"].split("'", 1)[1].split("'", 1)[0]
        store = link.split(".fr/", 1)[1].split("-", 1)[0]

        address = str(loc.find("div", {"class": "zoneText"}))
        address = re.sub(cleanr, " ", address).strip().split("\n", 1)[0]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            hours = (
                soup.find("li", {"class": "prefooter-listItemHoraires"})
                .text.replace("\n", " ")
                .strip()
            )
        except:
            hours = "<MISSING>"
        pa = parse_address_intl(address)

        street_address = pa.street_address_1
        street = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        pcode = zip_postal.strip() if zip_postal else MISSING

        ccode = pa.country
        ccode = ccode.strip() if ccode else MISSING

        yield SgRecord(
            locator_domain="https://www.supermarchesmatch.fr/",
            page_url=url,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours,
            raw_address=address,
        )


def scrape():
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
