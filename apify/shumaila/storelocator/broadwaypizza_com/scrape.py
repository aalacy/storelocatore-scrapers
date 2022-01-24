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
    cleanr = re.compile(r"<[^>]+>")
    pattern = re.compile(r"\s\s+")
    url = "https://www.broadwaypizza.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "location-block-2"})
    for div in divlist:
        title = div.find("h2").text
        link = "https://www.broadwaypizza.com" + div["href"]
        content = div.find("p", {"class": "location-page-text"})
        content = re.sub(cleanr, "\n", str(content))
        content = re.sub(pattern, "\n", str(content)).strip().splitlines()
        if len(content) == 3:
            street = content[0]
            city, state = content[1].split(", ", 1)
        elif len(content) == 4:
            street = content[0] + " " + content[1]
            city, state = content[2].split(", ", 1)
        else:
            continue
        state, pcode = state.split(" ", 1)

        phone = content[-1]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        longt, lat = (
            soup.find("div", {"class": "location-column-1"})
            .find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!3m", 1)[0]
            .split("!3d", 1)
        )

        daylist = (
            soup.find("div", {"class": "ms-big-hours-columns"})
            .find("div", {"class": "ms-big-hours-column---day"})
            .findAll("p")
        )
        timelist = (
            soup.find("div", {"class": "ms-big-hours-columns"})
            .find("div", {"class": "ms-big-hours-column---hours"})
            .findAll("p")
        )
        hours = ""
        for i in range(0, len(daylist)):
            hours = hours + daylist[i].text + " " + timelist[i].text + " "
        try:
            lat = lat.split("!", 1)[0]
        except:
            pass
        if " 200 S" in street:
            street = "200 S " + street.split(" 200 S", 1)[1]
        yield SgRecord(
            locator_domain="https://www.broadwaypizza.com/",
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
