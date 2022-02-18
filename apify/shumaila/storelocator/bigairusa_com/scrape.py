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
    url = "https://www.bigairusa.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.find("section", {"data-id": "3d481e14"}).findAll("a")
    for link in linklist:
        link = link["href"]
        if ("http") in link:
            continue
        else:
            link = "https://www.bigairusa.com" + link
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = soup.find("ul", {"class": "elementor-icon-list-items"})
        title = content.find("a").text
        phone = content.findAll("span")[-1].text
        try:
            hours = (
                "Monday "
                + soup.select_one('section:contains("Monday")')
                .text.split("Monday", 1)[1]
                .split("Info", 1)[0]
            )
            hours = re.sub(pattern, "\n", str(hours)).replace("\n", " ").strip()
        except:
            hrlink = link + "hours/"

            r2 = session.get(hrlink, headers=headers)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            hours = "MONDAY " + soup2.text.split("MONDAY", 1)[1].split("Holidays", 1)[0]
            hours = re.sub(pattern, "\n", str(hours)).replace("\n", " ").strip()
        try:
            hours = hours.split("Calender", 1)[0]
        except:
            pass
        try:
            lat, longt = (
                content.find("a")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )
            longt = longt.split(",", 1)[0]
            addrlink = content.find("a")["href"]
            r3 = session.get(addrlink)
            soup3 = BeautifulSoup(r3.text, "html.parser")
            address = (
                soup3.find("meta", {"itemprop": "name"})["content"]
                .split("· ", 1)[1]
                .split(", ")
            )
            street = address[0]
            city, state = title.split(", ", 1)
            pcode = address[-1].split(" ", 1)[1]
        except:

            try:
                addrlink = soup.select_one('a:contains("Directions")')["href"]
                r3 = session.get(addrlink, headers=headers)
                soup3 = BeautifulSoup(r3.text, "html.parser")
                addrlink = soup3.select_one("iframe[src*=embed]")["src"]

                r = session.get(addrlink, headers=headers)
                address = (
                    r.text.split('"Big Air ')[2].split(", ", 1)[1].split("]", 1)[0]
                )
                street, city, state = address.split('"', 1)[0].split(", ")
                lat, longt = address.split("[", 1)[1].split(",", 1)
                state, pcode = state.split(" ", 1)
            except:
                city, state = title.split(", ", 1)
                street = pcode = "<MISSING>"
                if "Greenville" in city:
                    street = "36 Park Woodruff Dr"
                    pcode = "29607"
        yield SgRecord(
            locator_domain="https://www.bigairusa.com/",
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
