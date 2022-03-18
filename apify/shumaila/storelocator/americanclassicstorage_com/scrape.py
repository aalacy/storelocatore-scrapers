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

    url = "https://www.americanclassicstorage.com/sitemap.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("loc")
    for link in linklist:
        link = link.text

        try:

            if (
                "/storage-units/" not in link
                or len(link.split("/storage-units/", 1)[1].split("/")) < 4
            ):
                continue
        except:
            continue
        r = session.get(link, headers=headers)
        content = r.text.split('type="application/ld+json">', 1)[1].split(
            "</script", 1
        )[0]
        content = json.loads(content)
        content = content[2]

        title = content["name"]

        street = content["address"]["streetAddress"]
        state = content["address"]["addressRegion"]
        pcode = content["address"]["postalCode"]
        city = content["address"]["addressLocality"]
        lat = content["geo"]["latitude"]
        longt = content["geo"]["longitude"]

        phone = content["contactPoint"][0]["telephone"]

        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
        hourslist = content["openingHoursSpecification"]
        hours = ""
        for hr in hourslist:
            day = hr["dayOfWeek"].replace("http://schema.org/", "")
            openstr = hr["opens"] + " am - "
            if openstr.split(":", 1)[0] == "00":
                hours = hours + day + " Closed"
            else:
                closestr = hr["closes"]
                close = int(closestr.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + openstr
                    + str(close)
                    + ":"
                    + closestr.split(":", 1)[1]
                    + " pm "
                )
        store = link.split("-")[-1].replace("/", "")

        yield SgRecord(
            locator_domain="https://www.americanclassicstorage.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours.replace(":00 am", " am")
            .replace(":00 pm", " pm")
            .replace("Closed", "Closed "),
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
