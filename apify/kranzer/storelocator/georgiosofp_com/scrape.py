from bs4 import BeautifulSoup
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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.georgiosofp.com/locations1"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.findAll("div", {"class": "sqs-block-content"})

    for div in divlist:

        if "MAPMENU" in div.text:
            pass
        else:
            continue
        content = re.sub(cleanr, "\n", str(div))
        content = re.sub(pattern, "\n", str(content)).strip().splitlines()
        title = content[0]
        address = content[1]
        try:
            street, city, state = address.split(", ", 2)
        except:
            street, state = address.split(", ", 1)
            city = street.strip().split(" ")[-1]
            street = street.replace(city, "")
        try:
            state, pcode = state.strip().split(" ", 1)
        except:
            pcode = "<MISSING>"
        phone = content[2]

        try:
            lat, longt = (
                div.select_one("a[href*=maps]")["href"]
                .split("@", 1)[1]
                .split("data", 1)[0]
                .split(",", 1)
            )

            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        if len(state) > 3:
            street = street + " " + city
            city = state
            temp, pcode = pcode.split(", ")
            city = city + " " + temp
            state, pcode = pcode.split(" ", 1)
        yield SgRecord(
            locator_domain="https://www.georgiosofp.com/",
            page_url=url,
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
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
