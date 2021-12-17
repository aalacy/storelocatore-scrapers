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

    url = "https://bestbrains.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "mapBorder"})
    for div in divlist:
        store = div["id"]
        title = div.find("h3").text
        street = soup.find("input", {"name": "aline" + store})["value"]
        city = soup.find("input", {"name": "acity" + store})["value"]
        state = soup.find("input", {"name": "astate" + store})["value"]
        ccode = soup.find("input", {"name": "acountry" + store})["value"]
        pcode = soup.find("input", {"name": "azipcode" + store})["value"]
        lat = soup.find("input", {"name": "alatitude" + store})["value"]
        longt = soup.find("input", {"name": "alongitude" + store})["value"]
        phone = soup.find("input", {"name": "aphoneno" + store})["value"]
        link = (
            "https://bestbrains.com"
            + div.find("div", {"class": "location-link"}).find("a")["href"]
        )
        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "html.parser")
        hours = (
            soup1.find("div", {"class": "center-timings"})
            .text.replace("\n", " ")
            .strip()
        )
        if "USA" in ccode:
            ccode = "US"
        elif "CAN" in ccode:
            ccode = "CA"
        yield SgRecord(
            locator_domain="https://bestbrains.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=str("<MISSING>"),
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
