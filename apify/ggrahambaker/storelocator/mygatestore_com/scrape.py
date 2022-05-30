from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data(sgw: SgWriter):
    # Your scraper here
    url = "https://mygatestore.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1647159501734"
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    storelist = soup.find("store").findAll("item")
    for store in storelist:
        title = store.find("location").text
        address = (
            store.find("address")
            .text.replace("&#44;", ",")
            .replace("  ", ",")
            .replace(",,", ",")
            .strip()
        )
        try:
            address1 = address.split(", USA")[1].split(",")
        except:
            pass

        address = address.split(", USA")[0].split(",")

        street = address[0]
        city = address[1]
        state = address[2].split()[0]
        try:
            pcode = address[2].split()[1]
        except:
            pcode = address1[-1].split()[1]

        lat = store.find("latitude").text
        longt = store.find("longitude").text
        try:
            storeid = title.split("#")[1]
        except:
            storeid = title.split(" ")[-1]

        sgw.write_row(
            SgRecord(
                locator_domain="https://mygatestore.com/",
                page_url="https://mygatestore.com/find-a-gate/",
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=storeid,
                phone="",
                location_type="",
                latitude=lat,
                longitude=longt,
                hours_of_operation="",
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
