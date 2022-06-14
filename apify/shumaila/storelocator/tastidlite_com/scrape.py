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

    url = "https://locator.kahalamgmt.com/locator/index.php?brand=23&mode=map&latitude=27.6648274&longitude=-81.5157535"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = str(soup.findAll("script", {"type": "text/javascript"})[1]).split("= {")
    for div in divlist:

        content = "{" + str(div).split("}", 1)[0] + "}"
        try:
            content = json.loads(content.replace("'", '"'))
        except:
            continue
        store = str(content["StoreId"])
        lat = str(content["Latitude"])
        longt = str(content["Longitude"])
        street = content["Address"]
        city = content["City"]
        state = content["State"]
        pcode = content["Zip"]
        phone = content["Phone"]
        title = "Tasti D-Lite #" + store
        if len(phone) < 3:
            phone = "<MISSING>"
        link = "https://www.tastidlite.com/stores//" + str(store)
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours = (
            soup.text.split("Hours", 1)[1]
            .split("Contact", 1)[0]
            .replace("PM", " PM ")
            .replace("AM", " AM ")
            .strip()
        )

        yield SgRecord(
            locator_domain="https://www.tastidlite.com/",
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
