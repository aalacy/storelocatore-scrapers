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

    url = "https://www.streetcorner.com/consumer/"
    page = session.get(url, headers=headers)
    cleanr = re.compile("<.*?>")
    loclist = page.text.split('<a href="https://www.streetcorner.com/store/')

    for loc in loclist:
        if loc.find("!DOCTYPE html>") == -1:
            link = "https://www.streetcorner.com/store/" + loc.split('"', 1)[0]

            try:
                page = session.get(link, headers=headers)
            except:
                continue
            try:
                coord = str(page.text).split("center: {lat:")[2]
            except:
                continue
            lat, longt = coord.split("}", 1)[0].split(", lng: ")
            soup1 = BeautifulSoup(page.text, "html.parser")
            title = soup1.find("span", {"itemprop": "name"}).text
            try:
                street = soup1.find("span", {"itemprop": "streetAddress"}).text
            except:
                street = "<MISSING>"
            try:
                city = soup1.find("span", {"itemprop": "addressLocality"}).text
            except:
                city = "<MISSING>"
            try:
                state = soup1.find("span", {"itemprop": "addressRegion"}).text
            except:
                state = "<MISSING>"
            try:
                pcode = soup1.find("span", {"itemprop": "postalCode"}).text
            except:
                pcode = "<MISSING>"
            try:
                phone = soup1.find("span", {"itemprop": "telephone"}).text
            except:
                phone = "<MISSING>"
            try:
                hours = soup1.find("span", {"itemprop": "openingHours"})
                hours = re.sub(cleanr, "\n", str(hours)).replace("\n", " ").lstrip()
                if hours == "None":
                    hours = "<MISSING>"
            except:

                hours = "<MISSING>"
            if len(phone) < 3:
                phone = "<MISSING>"
            if len(street) < 2:
                street = "<MISSING>"
            if len(pcode) < 2:
                pcode = "<MISSING>"
            else:
                if len(pcode) == 4:
                    pcode = "0" + pcode
            hours = hours.encode("ascii", "ignore").decode("ascii")
            if title.find("Coming Soon") == -1:

                yield SgRecord(
                    locator_domain="https://www.streetcorner.com/",
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
                    hours_of_operation=hours.replace("am", "am-"),
                )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
