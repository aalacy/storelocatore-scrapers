from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    session = SgRequests()

    url = "https://donatos.com/sitemap.xml"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")

    for link in linklist:
        if "locations/" not in link.text or "locations/all" in link.text:
            continue
        link = link.text

        session = SgRequests()
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        div = soup.find("main", {"id": "location-details"})
        try:
            title = div.find("h2").text
        except:
            continue
        street = div.find("span", {"itemprop": "streetAddress"}).text
        city = div.find("span", {"itemprop": "addressLocality"}).text
        state = div.find("span", {"itemprop": "addressRegion"}).text
        pcode = div.find("span", {"itemprop": "postalCode"}).text
        phone = div.find("dd", {"itemprop": "phone"}).text
        lat = r.text.split('data-lat="', 1)[1].split('"', 1)[0]
        longt = r.text.split('data-lng="', 1)[1].split('"', 1)[0]
        store = div.find("a", {"class": "btn"})["href"].split("=", 1)[1]
        hours = (
            div.text.split("Hours", 1)[1]
            .split("Order ", 1)[0]
            .replace("\n", " ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://donatos.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
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
