import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):
    # Your scraper here
    pattern = re.compile(r"\s\s+")
    url = "https://www.ucbi.com/locations/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    divlist = soup.findAll("article")

    for div in divlist:
        store = div["data-id"]
        lat = div["data-lat"]
        longt = div["data-lng"]
        street = div["data-street"]

        try:
            city = div["data-citystatezip"]
            city, state = city.split(", ", 1)
            state, pcode = state.lstrip().split(" ", 1)
        except:
            city = ""

        title = div["aria-label"]
        link = "https://www.ucbi.com" + div.find("a")["href"]
        ltype = div.find("div", {"class": "options"}).text
        if "Branch" in ltype or "Office" in ltype:
            ltype = ltype.lstrip().replace("\n", "|")
        else:
            continue
        if ltype[-1:] == "|":
            ltype = ltype[:-1]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        try:
            phone = soup.find("p", {"itemprop": "telephone"}).text

        except:
            phone = "<MISSING>"
        try:
            hours = soup.find("ul", {"itemprop": "openingHoursSpecification"}).text
            hours = re.sub(pattern, " ", hours)
            hours = hours.replace("\n", "").strip()
        except:
            hours = "<MISSING>"

        ltype = ltype.replace("Branch|", "Branch")
        try:
            phone = phone.split(" (1-", 1)[1].split(")", 1)[0]
        except:
            pass

        if not city:
            city = soup.find("span", {"itemprop": "addressLocality"}).text
            state = soup.find("span", {"itemprop": "addressRegion"}).text
            pcode = soup.find("span", {"itemprop": "postalCode"}).text

        sgw.write_row(
            SgRecord(
                locator_domain="https://www.ucbi.com",
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode.strip(),
                country_code="US",
                store_number=store,
                phone=phone,
                location_type=ltype,
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
