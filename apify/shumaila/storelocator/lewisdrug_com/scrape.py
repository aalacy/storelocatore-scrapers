from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.lewisdrug.com/stores"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "store-location"})
    for div in divlist:
        link = div.find("h3").find("a")["href"]

        title = div.find("h3").text.strip()
        address = div.find("div", {"class": "address"}).text
        address = re.sub(pattern, "\n", str(address)).strip().splitlines()

        street = address[0]
        if len(address) == 2:
            city, state = address[1].split(", ", 1)
        elif len(address) == 3:
            street = street + " " + address[1]
            city, state = address[2].split(", ", 1)
        state, pcode = state.split(" ", 1)
        state = state.replace(",", "")
        if state in pcode:
            pcode = pcode.replace(state, "")
        phone = div.select_one("a[href*=tel]").text

        r = session.get(link, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        lat = r.text.split('"latitude": "')[-1].split('"', 1)[0]
        longt = r.text.split('"longitude": "')[-1].split('"', 1)[0]

        hours = soup.find("div", {"class": "hours"}).text
        hours = (
            re.sub(pattern, " ", str(hours))
            .replace("\n", " ")
            .split("Mon", 1)[1]
            .strip()
        )
        hours = "Mon " + hours.encode("ascii", "ignore").decode("ascii")

        yield SgRecord(
            locator_domain="https://www.lewisdrug.com/",
            page_url=link,
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
