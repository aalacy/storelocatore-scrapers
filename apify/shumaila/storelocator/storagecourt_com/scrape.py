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

    url = "https://www.storagecourt.com/self-storage"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    linklist = soup.findAll("a", {"class": "ogep3VRb_llXipWczX6wu"})
    for link in linklist:
        title = link.text
        link = "https://www.storagecourt.com" + link["href"]

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        content = r.text.split(link.split("/")[-1] + '","address":', 1)[1].split(
            '},"', 1
        )[0]
        content = content + "}"
        content = json.loads(content)

        street = content["streetAddress"]
        city = content["addressLocality"]
        pcode = content["postalCode"]
        state = content["addressRegion"]
        ccode = "US"

        lat = r.text.split('"latitude":', 1)[1].split(",", 1)[0]
        longt = r.text.split('"longitude":', 1)[1].split(",", 1)[0]
        phone = r.text.split('},"phone":"', 1)[1].split('"', 1)[0]
        hours = (
            soup.text.split("OFFICE HOURS", 1)[1]
            .split("ACCESS HOURS", 1)[0]
            .replace("pm", "pm ")
        )
        hours = re.sub(pattern, " ", hours).strip()
        try:
            hours = hours.split("(", 1)[0]
        except:
            pass
        ltype = "Store"
        if "Storage Court" in title:
            pass
        else:
            ltype = "Dealer"
        yield SgRecord(
            locator_domain="https://www.storagecourt.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=ltype,
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
