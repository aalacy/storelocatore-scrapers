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
    url = "https://www.thistle.com/find-your-hotel"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "read-more-link"})
    loclist = soup.findAll("div", {"class": "map-poi"})
    for link in linklist:
        title = link["aria-label"]
        link = link["href"]
        for loc in loclist:
            if loc["data-name"] in title:

                title = loc["data-name"]
                lat = loc["data-lat"]
                longt = loc["data-lng"]
                street = loc["data-address"]
                city = loc["data-city"]
                pcode = loc["data-zipcode"]
                if " London" in street:
                    street = street.split(" London", 1)[0]
                    city = "London"
                elif " Poole " in street:

                    street, pcode = street.split(" Poole ", 1)
                    city = "Poole"
                yield SgRecord(
                    locator_domain="https://www.thistle.com/",
                    page_url=link,
                    location_name=title,
                    street_address=street.strip(),
                    city=city.strip(),
                    state=SgRecord.MISSING,
                    zip_postal=pcode.strip(),
                    country_code="GB",
                    store_number=SgRecord.MISSING,
                    phone=SgRecord.MISSING,
                    location_type=SgRecord.MISSING,
                    latitude=str(lat),
                    longitude=str(longt),
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
