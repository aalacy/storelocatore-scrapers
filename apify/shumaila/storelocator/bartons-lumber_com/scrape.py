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

    url = "https://www.bartons-lumber.com/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    divlist = soup.find("nav", {"id": "HeaderNavigation"}).select("a[href*=locations]")

    for div in divlist:
        title = div.text
        link = "https://www.bartons-lumber.com" + div["href"]
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("div", {"class": "HTMLContent"})
        address = content.findAll("p")[0].text
        street, city, state = address.split(", ", 2)
        state, pcode = state.split(" ", 1)
        pcode, phone = pcode.split("(", 1)
        phone = "(" + phone.strip()
        if "OPEN" in phone:
            phone, hours = phone.split("OPEN:", 1)
        else:
            hours = content.findAll("p")[1].text
        longt, lat = (
            content.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d", 1)
        )
        hours = hours.replace("OPEN:", "").strip()
        try:
            street = street.split("(", 1)[0]
        except:
            pass
        if "Paragould" in title:
            pcode = "72450"
        yield SgRecord(
            locator_domain="https://www.bartons-lumber.com/",
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
