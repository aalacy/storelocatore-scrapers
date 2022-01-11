import lxml
from bs4 import BeautifulSoup

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.lexus.com.kw/.rest/toyota/locations?lang=ar&path=/lexus"
    domain = "lexus.com.kw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    soup = BeautifulSoup(response.text, "lxml")

    all_locations = soup.find_all("branchitem")
    for poi in all_locations:
        geo = poi.find("getdirection").text.split("=")[-1].split(",")
        location_name = poi.find("name").text
        phone = lxml.etree.HTML(poi.find("phone_no").text).xpath("//text()")[0]
        if phone.startswith("("):
            phone = ""
        location_type = poi.find("sdisplayname").text
        hoo = lxml.etree.HTML(poi.find("working_days").text).xpath("//text()")
        hoo = [e.strip() for e in hoo]
        hoo = " ".join(" ".join(hoo).split())
        if not phone and "-------" in hoo:
            phone = hoo.split("-------")[0].split()[-1]
        if phone:
            hoo = hoo.split(phone)[0].strip().replace("(", "").replace(")", "")

        item = SgRecord(
            locator_domain=domain,
            page_url="https://www.lexus.com.kw/lexus/locations.html",
            location_name=location_name,
            street_address="",
            city="",
            state="",
            zip_postal="",
            country_code="KW",
            store_number="",
            phone=phone,
            location_type=location_type,
            latitude=geo[0],
            longitude=geo[1],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.LATITUDE})
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
