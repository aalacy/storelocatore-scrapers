from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.mightyfineburgers.com/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("a", {"class": "image-slide-anchor"})

    for div in divlist:

        try:
            if "https:" not in div["href"]:
                link = "https://www.mightyfineburgers.com" + div["href"]
            else:
                link = div["href"]
        except:
            continue
        if "feedback" in link:
            continue
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = r.text.split('data-block-json="', 1)[1].split(';"', 1)[0]
        content = (
            content.replace("&#123;", "{")
            .replace("&quot;", '"')
            .replace("&#125", "}")
            .replace("};,", "},")
            .replace(";}", "}")
        )
        content = json.loads(content)
        content = content["location"]
        title = r.text.split('"fullSiteTitle":"', 1)[1].split("\\u2014 ", 1)[0]
        street = content["addressLine1"]
        city, state = content["addressLine2"].split(",", 1)
        state, pcode = state.lstrip().split(" ", 1)
        lat = content["markerLat"]
        longt = content["markerLng"]
        hours, phone = soup.text.split("Monday", 1)[1].split("\n", 1)[0].split("(")
        hours = "Monday " + hours.replace("PM", "PM ")
        phone = "(" + phone
        if "1335 E Whitestone" in street:
            street = street + "  Suite 100"
        yield SgRecord(
            locator_domain="https://www.mightyfineburgers.com",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.replace("\xa0", "").strip(),
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
