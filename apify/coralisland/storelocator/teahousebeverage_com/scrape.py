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
    cleanr = re.compile(r"<[^>]+>")
    url = "http://teahousebeverage.com/locations/"

    r = session.get(url, headers=headers)
    loclist = r.text.split('{"map_id":"')[1:]
    for loc in loclist:
        loc = loc.split("}", 1)[0]
        loc = "{" + loc.split(",", 1)[1] + "}"
        loc = json.loads(loc)
        store = loc["marker_id"]
        title = loc["title"]
        address = loc["address"]
        address = re.sub(cleanr, "\n", address)
        address = re.sub(pattern, "\n", address).replace(", United States", "").strip()
        address = address.replace("\n", ", ")

        try:
            street, city, state = address.split(", ", 2)
            state, pcode = state.split(" ", 1)
            state = state.replace(",", "")
        except:
            try:
                street, city = address.split(", ", 1)
                city, state = city.strip().split(" ", 1)
                state, pcode = state.split(" ", 1)
                state = state.replace(",", "")
            except:
                street = address
                city = pcode = "<MISSING>"
                state = "TX"
        lat = loc["lat"]
        longt = loc["lng"]
        content = loc["desc"]
        content = re.sub(cleanr, "\n", content)
        content = re.sub(pattern, "\n", content).strip()

        try:
            phone = content.split("\n", 1)[0]
            hours = content.split("\n", 1)[1]
        except:
            phone = hours = "<MISSING>"
        try:
            hours = hours.split("Holiday", 1)[0]
        except:
            pass
        hours = hours.replace("\n", " ").strip()
        if "USA" in pcode:
            pcode = "<MISSING>"
        if "Suite" in pcode:
            pcode, temp = pcode.split(", ", 1)
            street = street + " " + temp
        yield SgRecord(
            locator_domain="http://teahousebeverage.com/",
            page_url=url,
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
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
