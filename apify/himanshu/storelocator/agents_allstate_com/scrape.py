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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://agents.allstate.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    mainlist = soup.findAll("loc")
    for mlink in mainlist:
        mlink = mlink.text
        r = session.get(mlink, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("loc")
        for link in linklist:
            link = link.text

            if (".amp.") in link:
                continue
            if len(link.split("/")) > 4:
                continue
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                street = soup.find("span", {"class": "c-address-street-1"}).text
                try:
                    street = (
                        street
                        + " "
                        + soup.find("span", {"class": "c-address-street-2"}).text
                    )
                except:
                    pass
                city = soup.find("span", {"class": "c-address-city"}).text
                state = soup.find("abbr", {"class": "c-address-state"}).text
                pcode = soup.find("span", {"class": "c-address-postal-code"}).text
                lat = soup.find("meta", {"itemprop": "latitude"})["content"]
                longt = soup.find("meta", {"itemprop": "longitude"})["content"]
            except:
                street = pcode = lat = longt = "<MISSING>"
                try:
                    city, state = soup.find("span", {"class": "Hero-geo"}).text.split(
                        ", "
                    )
                except:
                    continue
            try:
                phone = soup.findAll("span", {"class": "Core-phoneText"})[-1].text
            except:
                phone = "<MISSING>"
            try:
                hours = soup.find("table", {"class": "c-hours-details"})
                hours = re.sub(cleanr, "\n", str(hours))
                hours = (
                    re.sub(pattern, " ", str(hours))
                    .replace("Day of the Week Hours", "")
                    .replace("Available by appointment", "")
                    .replace("PM", "PM ")
                    .replace("Closed", " Closed ")
                    .strip()
                )
            except:
                hours = "<MISSING>"
            if "None" in hours:
                hours = "<MISSING>"
            title = soup.find("span", {"class": "MiniHero-name"}).text
            title = title.encode("ascii", "ignore").decode("ascii")
            yield SgRecord(
                locator_domain="https://agents.allstate.com/",
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
