from bs4 import BeautifulSoup
import usaddress
import re
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.sleepexperts.com/stores"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    store_list = soup.findAll("div", {"class": "StorePromo"})
    pattern = re.compile(r"\s\s+")
    for store in store_list:
        title = store.find("div", {"class": "StorePromo-title"}).text
        address = store.find("div", {"class": "StorePromo-address"}).text

        try:
            phone = store.find("div", {"class": "StorePromo-phoneNumber"}).text
        except:
            phone = "<MISSING>"
        try:
            hours = store.find("div", {"class": "StorePromo-condensedHours"}).text
        except:
            hours = "<MISSING>"
        hours = re.sub(pattern, "\n", hours).replace("\n", " ").strip()
        link = store.find("a", {"class": "StorePromo-cta"})["href"]
        address = usaddress.parse(address)
        i = 0
        street = ""
        city = ""
        state = ""
        pcode = ""
        while i < len(address):
            temp = address[i]
            if (
                temp[1].find("Address") != -1
                or temp[1].find("Street") != -1
                or temp[1].find("Recipient") != -1
                or temp[1].find("BuildingName") != -1
                or temp[1].find("USPSBoxType") != -1
                or temp[1].find("USPSBoxID") != -1
            ):
                street = street + " " + temp[0]
            if temp[1].find("PlaceName") != -1:
                city = city + " " + temp[0]
            if temp[1].find("StateName") != -1:
                state = state + " " + temp[0]
            if temp[1].find("ZipCode") != -1:
                pcode = pcode + " " + temp[0]
            i += 1
        yield SgRecord(
            locator_domain="https://www.sleepexperts.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude="<INACCESSIBLE>",
            longitude="<INACCESSIBLE>",
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
