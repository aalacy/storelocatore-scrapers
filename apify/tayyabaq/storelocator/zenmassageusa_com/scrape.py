import re
from bs4 import BeautifulSoup
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
    cleanr = re.compile(r"<[^>]+>")
    url = "https://www.zenmassageusa.com/wp-admin/admin-ajax.php?action=store_search&lat=35.323753&lng=-80.655902&max_results=NaN&radius=100&autoload=1"
    loclist = session.get(url, headers=headers).json()
    for loc in loclist:
        store = loc["id"]
        title = loc["store"]
        street = loc["address"] + " " + str(loc["address2"])
        city = loc["city"]
        state = loc["state"]
        pcode = loc["zip"]
        phone = loc["phone"]
        lat = loc["lat"]
        longt = loc["lng"]
        hours = loc["hours"]
        hours = re.sub(cleanr, " ", hours).replace("\n", " ").strip()
        link = loc["url"]
        if len(phone) < 3:
            r = session.get(link, headers=headers)
            r.encoding = "utf-8-sig"
            soup = BeautifulSoup(r.text, "html.parser").text
            phone = (
                soup.split("Call:", 1)[1]
                .split("\n", 1)[1]
                .split("\n", 1)[0]
                .replace("\n", "")
                .strip()
            )
            hours = (
                soup.split("Hours of Operation", 1)[1]
                .split("Spa", 1)[0]
                .replace("\n", " ")
                .replace(": Mon", "Mon")
                .strip()
            )
            hours = (
                str(hours.encode(encoding="ascii", errors="replace"))
                .replace("?", "-")
                .replace("b'", "")
                .strip()
                .replace("'", "")
                .replace("-- ", "-")
            )
        yield SgRecord(
            locator_domain="https://www.zenmassageusa.com/",
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
