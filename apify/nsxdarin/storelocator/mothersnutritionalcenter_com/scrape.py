import json
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


from sglogging import SgLogSetup


logger = SgLogSetup().get_logger("bluefcu_com")


def fetch_data():

    url = "https://mothersnc.pixelatedarts.net/assets/files/stores-map.js"
    r = session.get(url, headers=headers)
    hourslist = r.text.split("var locations = ", 1)[1].split(";var storeLocations", 1)[
        0
    ]
    hourslist = json.loads(hourslist)

    for hr in hourslist:

        divlist = BeautifulSoup(str(hr[0]), "html.parser").findAll("p")
        title = divlist[0].text
        hours = divlist[1].text.replace("Store Hours:", "").strip()
        address = divlist[2].text
        street, city = address.split(", ", 1)
        pcode = city.split(" ")[-1]
        state = city.split(" ")[-2]
        city = city.split(" " + state, 1)[0]
        phone = divlist[3].text
        store = title.split("Store ", 1)[1]
        lat = hr[1]
        longt = hr[2]

        yield SgRecord(
            locator_domain="https://mothersnutritionalcenter.com/",
            page_url="https://mothersnc.com/pages/stores/",
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
