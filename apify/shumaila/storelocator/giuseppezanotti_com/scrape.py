from bs4 import BeautifulSoup
import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.giuseppezanotti.com/wo/store-finder/"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("select", {"id": "storeFinderSelectCountry"}).findAll("option")[
        1:
    ]
    for div in divlist:
        ccode = div["value"]
        url = "https://www.giuseppezanotti.com/wo/amlocator/index/ajax/"
        headers["x-requested-with"] = "XMLHttpRequest"
        dataobj = {
            "mapId": "amlocator-map-canvas626078c0bb65f",
            "storeListId": "amlocator_store_list626078c0bb12a",
            "product": "0",
            "category": "0",
            "attributes[0][name]": "1",
            "attributes[0][value]": "1",
            "attributes[1][name]": "1",
            "attributes[1][value]": "2",
            "attributes[2][name]": "1",
            "attributes[2][value]": "3",
            "country": ccode,
        }

        loclist = session.post(url, headers=headers, data=dataobj).json()["items"]
        for loc in loclist:

            store = loc["id"]
            title = loc["name"]
            ccode = loc["country"]
            city = loc["city"]
            try:
                pcode = loc["zip"].strip()
            except:
                pcode = "<MISSING>"
            raw_address = loc["address"].replace("'", "")

            lat = loc["lat"]
            longt = loc["lng"]
            try:
                state = loc["state"].strip()
            except:
                state = "<MISSING>"
            try:
                phone = loc["phone"].strip()
            except:
                phone = "<MISSING>"
            if "null" in pcode.lower():
                pcode = "<MISSING>"
            try:
                hourslist = json.loads(loc["schedule_string"])
                hours = ""
                for hr in hourslist:
                    day = hr
                    start = (
                        hourslist[day]["from"]["hours"]
                        + ":"
                        + hourslist[day]["from"]["minutes"]
                    )
                    endstr = (
                        hourslist[day]["to"]["hours"]
                        + ":"
                        + hourslist[day]["to"]["minutes"]
                    )
                    hours = hours + day + " " + start + " - " + endstr + " "
            except:
                hours = "<MISSING>"
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street = street_address if street_address else MISSING

            link = (
                "https://www.giuseppezanotti.com/wo/store-finder/"
                + loc["url_key"]
                + "/"
            )
            yield SgRecord(
                locator_domain="https://www.giuseppezanotti.com",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type=SgRecord.MISSING,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
                raw_address=raw_address,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
