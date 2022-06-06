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
    url = "https://www.serviceking.com/locations?view=see-all"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"geoPoints":', 1)[1].split("}]", 1)[0]
    loclist = loclist + "}]"
    loclist = json.loads(loclist)
    for loc in loclist:
        store = loc["nid"]
        title = loc["title"]
        street = loc["address"]
        city = loc["city"]
        city, state = city.split(", ", 1)
        pcode = loc["zip"]
        lat = loc["lat"]
        longt = loc["lng"]
        phone = loc["phone"]
        try:
            if len(phone) < 3:
                phone = "<MISSING>"
        except:
            phone = "<MISSING>"
        try:
            if pcode.strip().isdigit():
                ccode = "US"
            else:
                ccode = "CA"
        except:
            pcode = "<MISSING>"
            ccode = "US"
        link = "https://www.serviceking.com" + loc["alias"]
        r = session.get(link, headers=headers)

        soup = BeautifulSoup(r.text, "html.parser")

        hours = (
            soup.find("div", {"class": "time-content"})
            .text.replace("pm", "pm ")
            .replace("Closed", "Closed ")
        )
        hours = re.sub(pattern, " ", hours).strip().replace("\n", " ")

        yield SgRecord(
            locator_domain="https://www.serviceking.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type="<MISSING>",
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
