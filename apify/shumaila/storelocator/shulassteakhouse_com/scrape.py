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
    url = "https://shulassteakhouse.com/#locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "shula-menu__location"})

    for div in divlist:
        if "shulassteakhouse" in div.find("a")["href"]:
            pass
        else:
            continue
        link = div.find("a")["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        title = (
            soup.find("div", {"class": "shula-block-split-content-title"})
            .find("h2")
            .text
        )
        content = soup.find("div", {"class": "shula-block-split-content-body"})
        content = re.sub(cleanr, "\n", str(content)).strip()
        content = re.sub(pattern, "\n", content).replace(" &amp; ", " & ").splitlines()
        m = 0
        street = content[m]
        try:
            city, state = content[m + 1].split(", ", 1)
        except:
            m = 2
            street = content[m]
            city, state = content[m + 1].split(", ", 1)
        state, pcode = state.lstrip().split(" ", 1)
        phone = content[m + 2].replace("Phone", "").replace(":", "")
        hours = " ".join(content[m + 3 :])
        if hours.find("temporarily closed") > -1:
            hours = "Temporarily Closed"
        else:
            if hours.find("Dine") > -1:
                hours = " ".join(content[m + 4 :])
        phone = phone.replace("Tel ", "")
        longt, lat = (
            soup.find("div", {"class": "embed-container"})
            .find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!2m", 1)[0]
            .split("!3d")
        )
        try:
            hours = hours.split(" Email Us", 1)[0]
        except:
            pass
        hours = hours.replace("Hours", "")

        yield SgRecord(
            locator_domain="https://shulassteakhouse.com/#locations",
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
