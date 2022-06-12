from bs4 import BeautifulSoup
import json
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

    url = "https://sbsu.com/branch-information"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.select("a[href*=branches]")
    for link in linklist:
        link = link["href"].replace("..", "https://sbsu.com")
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        longt, lat = (
            soup.find("iframe")["src"]
            .split("!2d", 1)[1]
            .split("!3m", 1)[0]
            .split("!3d", 1)
        )
        loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script>", 1
        )[0]
        loc = json.loads(loc.strip())
        title = loc["name"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        try:
            street = street + " " + loc["address"]["postOfficeBoxNumber"]
        except:
            pass
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        hourslist = soup.find("table").findAll("tr")[1:]
        hours = ""
        for hr in hourslist:
            day = hr.findAll("td")[0].text
            tstr = hr.findAll("td")[1].text
            hours = hours + day + " " + tstr + " "
        yield SgRecord(
            locator_domain="https://sbsu.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=str(state),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number="<MISSING>",
            phone=phone.strip(),
            location_type="Branch | ATM",
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
