from bs4 import BeautifulSoup
import json
import re
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
    url = "https://www.fishkeeper.co.uk/storefinder"
    r = session.get(url, headers=headers, verify=False)
    r = r.text.split(':{"stores":')[1].split(',"center"', 1)[0]
    r = r.replace("\n", "")
    loclist = json.loads(r)
    for loc in loclist:
        title = loc["title"]
        phone = loc["phone"]
        address = loc["address"]
        address = re.sub(pattern, "\n", address)
        pcode = address.split("\n")[-1]
        city = address.split("\n")[-2]
        street = " ".join(address.split("\n")[0:-2])
        state = loc["region"]
        lat = loc["lat"]
        longt = loc["lng"]
        link = loc["url"]
        store = loc["id"]
        hours = "<MISSING>"
        r = session.get(link, headers=headers, verify=False)
        try:
            hours = (
                BeautifulSoup(r.text, "html.parser")
                .find("table", {"class": "hours-table"})
                .text.replace("\n", " ")
                .replace("day", "day ")
                .replace(":00", ":00 ")
                .replace(":30", ":30 ")
                .strip()
            )
        except:
            hours = "<MISSING>"
        if "Due to" in hours:
            hours = "<MISSING>"
        if len(phone) < 3:
            phone = "<MISSING>"
        if len(pcode) < 2:
            pcode = city
            city = street.strip().split(" ")[-1]
        yield SgRecord(
            locator_domain="https://www.fishkeeper.co.uk/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.replace("\xa0", ""),
            country_code="UK",
            store_number=store,
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=lat,
            longitude=longt,
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
