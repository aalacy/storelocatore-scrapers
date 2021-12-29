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
    url = "https://wingstogo.com/all-locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "view-more"})
    for div in divlist:
        link = "https://wingstogo.com" + div.select_one("a[href*=location]")["href"]
        r = session.get(link, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")
        ltype = "<MISSING>"
        if "Opening Soon!" in soup.text:
            ltype = "Opening Soon"
        elif "STORE CLOSED" in soup.text:
            ltype = "STORE CLOSED"
        content = soup.find("div", {"class": "loc-details-full"})
        if "COMING SOON!" in content.text:
            continue
        title = (
            content.find("div", {"class": "loc-details-title"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        city = (
            content.find("span", {"class": "detail-city"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        street = (
            content.find("span", {"class": "detail-address"})
            .text.replace("\n", " ")
            .replace("\t", "")
            .strip()
        )
        try:
            phone = (
                content.find("span", {"class": "detail-phone"})
                .text.replace("\n", " ")
                .replace("\t", "")
                .strip()
            )
        except:
            phone = "<MISSING>"
        hours = (
            re.sub(cleanr, "\n", str(content.find("div", {"class": "location-hours"})))
            .replace("\n", " ")
            .replace("\t", "")
            .replace("Hours:  ", "")
            .strip()
        )
        try:
            longt, lat = (
                soup.find("div", {"class": "loc-details-map"})
                .find("iframe")["src"]
                .split("!2d", 1)[1]
                .split("!2m", 1)[0]
                .split("!3d", 1)
            )
        except:
            lat = longt = "<MISSING>"
        city, state = city.strip().split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        street = street.replace("Under New Management!!", "").strip()
        if "Permanently Closed " in street:
            ltype = "Permanently Closed"
            street = street.replace("Permanently Closed ", "")
        yield SgRecord(
            locator_domain="https://wingstogo.com/",
            page_url=link,
            location_name=re.sub(pattern, " ", title).strip(),
            street_address=re.sub(pattern, " ", street).strip(),
            city=re.sub(pattern, " ", city).strip(),
            state=re.sub(pattern, " ", state).strip(),
            zip_postal=re.sub(pattern, " ", pcode).strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=re.sub(pattern, " ", phone).strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=re.sub(pattern, " ", hours).strip(),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
