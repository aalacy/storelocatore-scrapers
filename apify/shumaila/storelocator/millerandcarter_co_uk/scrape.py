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

    url = "https://www.millerandcarter.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")
    for link in linklist:

        link = link.text

        try:
            check = link.split("/restaurants", 1)[1].split("/")

            if len(check) == 3:
                pass
            else:
                continue
        except:
            continue
        try:
            r = session.get(link, headers=headers)
        except:
            continue
        loc = r.text.split('<script type="application/ld+json">', 1)[1].split(
            "</script>", 1
        )[0]
        loc = json.loads(loc.replace("\n", ""))
        title = loc["name"]
        street = loc["address"]["streetAddress"]
        try:
            city = loc["address"]["addressLocality"]
        except:
            city = "<MISSING>"
        try:
            state = loc["address"]["addressRegion"]
        except:
            state = "<MISSING>"
        ccode = "GB"
        pcode = loc["address"]["postalCode"]
        phone = loc["telephone"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        hourlist = loc["openingHoursSpecification"]
        hours = ""
        for hr in hourlist:
            day = hr["dayOfWeek"][0]
            openstr = ""
            closestr = ""
            if int(hr["opens"].split(":", 1)[0]) == 12:
                openstr = "Midday - "
            else:
                openstr = hr["opens"].split(":", 1)[0] + " AM - "
            if int(hr["closes"].split(":", 1)[0]) > 12:
                closestr = str(int(hr["closes"].split(":", 1)[0]) - 12) + " PM "
            else:
                closestr = str(int(hr["closes"].split(":", 1)[0])) + " PM "
            hours = hours + day + " " + openstr + closestr
        yield SgRecord(
            locator_domain="https://www.millerandcarter.co.uk",
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
