from bs4 import BeautifulSoup
import re
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

    pattern = re.compile(r"\s\s+")
    url = "https://www.judesbarbershop.com/location/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("nav").select_one('li:contains("Locations")').findAll("li")

    for div in divlist:
        link = div.find("a")["href"]
        r = session.get(link, headers=headers)
        try:
            loclist = r.text.split('"@context": "https://schema.org",', 1)[1].split(
                "</script>", 1
            )[0]
        except:
            continue
        loclist = "{" + loclist
        loc = re.sub(pattern, "", loclist)
        loc = json.loads(loc)
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        phone = loc["telephone"]
        title = loc["name"]
        hourlist = loc["openingHoursSpecification"]
        hours = ""
        for hour in hourlist:
            start = (int)(hour["opens"].split(":")[0])
            if start > 12:
                start = start - 12
            endstr = (int)(hour["closes"].split(":")[0])
            if endstr > 12:
                endstr = endstr - 12
            try:
                hours = (
                    hours
                    + hour["dayOfWeek"]
                    + " "
                    + str(start)
                    + ":"
                    + hour["opens"].split(":", 1)[1]
                    + " AM - "
                    + str(endstr)
                    + ":"
                    + hour["closes"].split(":", 1)[1]
                    + " PM  "
                )
            except:
                hours = (
                    hours
                    + ", ".join(hour["dayOfWeek"])
                    + "="
                    + str(start)
                    + ":"
                    + hour["opens"].split(":", 1)[1]
                    + " AM - "
                    + str(endstr)
                    + ":"
                    + hour["closes"].split(":", 1)[1]
                    + " PM  "
                )
                break
        yield SgRecord(
            locator_domain="https://www.judesbarbershop.com",
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
