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

    url = "https://locations.tonyromas.com/sitemap"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    checklist = []
    linklist = soup.select("a[href*=canada]")
    linklist = linklist + soup.select("a[href*=united-states]")
    for link in linklist:
        link = link["href"]
        check = link.split("/")
        if len(check) < 4 or link in checklist:
            continue
        checklist.append(link)
        link = "https://locations.tonyromas.com/" + link
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        coord = soup.find("span", {"class": "coordinates"}).findAll("meta")
        lat = coord[0]["content"]
        longt = coord[1]["content"]
        title = soup.find("span", {"class": "LocationName"}).text
        address = soup.find("address", {"class": "c-address"}).findAll("meta")
        city = address[0]["content"]
        street = address[1]["content"]
        address = soup.find("address", {"class": "c-address"}).findAll("abbr")
        state = address[0].text
        ccode = address[1].text
        pcode = (
            soup.find("address", {"class": "c-address"})
            .find("span", {"class": "c-address-postal-code"})
            .text
        )
        phone = soup.find("span", {"id": "telephone"}).text
        try:
            hours = soup.find("table", {"class": "c-location-hours-details"}).text
            hours = (
                hours.split("Hours", 1)[1]
                .replace("Closed", "Closed ")
                .replace("day", "day ")
                .replace("PM", "PM ")
                .strip()
            )
        except:
            hours = "<MISSING>"
        store = r.text.split('"id"', 1)[1].split(":", 1)[1].split(",", 1)[0]

        yield SgRecord(
            locator_domain="https://tonyromas.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
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
