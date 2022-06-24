from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.peoplesjewellers.com/sitemap-20.xml"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "xml")
    linklist = soup.findAll("loc")
    for link in linklist:
        link = link.text
        r = session.get(link, headers=headers)
        try:
            loc = (
                r.text.split('<script type="application/ld+json">', 1)[1]
                .split("</script", 1)[0]
                .replace("\n", "")
                .strip()
            )
        except:
            continue
        loc = json.loads(loc)
        title = loc["name"]
        link = loc["@id"]
        phone = loc["telephone"]
        street = loc["address"]["streetAddress"]
        city = loc["address"]["addressLocality"]
        state = loc["address"]["addressRegion"]
        pcode = loc["address"]["postalCode"]
        ccode = loc["address"]["addressCountry"]
        lat = loc["geo"]["latitude"]
        longt = loc["geo"]["longitude"]
        hourslist = loc["openingHoursSpecification"]
        hours = ""
        for hr in hourslist:
            day = hr["dayOfWeek"]
            openstr = hr["opens"] + " am - "
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
        store = link.split("/")[-1]
        yield SgRecord(
            locator_domain="https://www.peoplesjewellers.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=store,
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=lat,
            longitude=longt,
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
