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
    url = "https://www.atriaseniorliving.com/retirement-communities?utm_source=redirectlink"
    r = session.get(url, headers=headers)
    loclist = (
        r.text.split("communityData:", 1)[1]
        .split(",communityDataSearch", 1)[0]
        .replace('"', "")
        .replace("{", '{"')
        .replace(":", '":"')
        .replace(",", '","')
        .replace("}", '"}')
        .replace('}","{', "},{")
        .replace("\\u002F", "\\")
        .replace('https":"\\', "https:\\")
        .replace("\\", "//")
        .replace(']"', "]")
        .replace(':"[', ":[")
    )

    loclist = json.loads(loclist)
    for loc in loclist:

        longt = loc["longitude"]
        lat = loc["latitude"]
        phone = loc["phoneNumber"].strip()
        store = loc["communityNumber"]
        title = loc["communityName"]
        street = loc["streetAddress"]
        link = "https://atriaseniorliving.com" + loc["url"].replace("//", "/")
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")

        address = soup.find("div", {"class": "address-div"}).text.strip()
        address = re.sub(pattern, "\n", address).strip().splitlines()

        pcode = address[-1]
        city = address[-3]
        state = address[-2]

        if len(longt) < 3:
            longt = r.text.split(',"ListItem","' + str(lat) + '","', 1)[1].split(
                '"', 1
            )[0]
        if len(str(store)) < 3:
            store = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.atriaseniorliving.com/",
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
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
