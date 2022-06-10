from bs4 import BeautifulSoup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.tobycarvery.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("loc")
    for div in divlist:
        link = div.text

        try:
            if len(link.split("/restaurants/", 1)[1].split("/")) == 2:
                pass
            else:
                continue
        except:
            continue
        r = session.get(link, headers=headers)
        try:
            loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
                "</script", 1
            )[0]
        except:
            continue
        loc = loc.replace("\n", "").strip()
        loc = json.loads(loc)
        title = loc["name"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        try:
            state = loc["address"]["addressRegion"]
        except:
            state = "<MISSING>"
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["addressCountry"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        hourslist = json.loads(str(loc["openingHoursSpecification"]).replace("'", '"'))
        hours = ""
        for hr in hourslist:
            opens = hr["opens"]
            closes = hr["closes"]
            if opens.split(":")[0] == "00":
                time = "Closed"
            else:
                time = opens + "-" + closes
            hours = hours + hr["dayOfWeek"][0] + " " + time + " "
        yield SgRecord(
            locator_domain="https://www.tobycarvery.co.uk/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
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
