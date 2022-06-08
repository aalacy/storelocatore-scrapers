from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://www.baptistonline.org"
base_url = "https://www.baptistonline.org/locations"


def find_details(link, location_type, session, sgw):
    page_url = link.a["href"]
    if "google.com" in page_url or "tel:" in page_url:
        page_url = SgRecord.MISSING
    elif not page_url.startswith("http"):
        page_url = locator_domain + link.a["href"]
    addr = list(link.select_one("p.location-address").stripped_strings)
    phone = SgRecord.MISSING
    store_number = SgRecord.MISSING
    hours_of_operation = SgRecord.MISSING
    if link.select_one(".location-phone"):
        phone = link.select_one(".location-phone").text.strip()
    location_name = link.select_one(".location-name").text.strip()
    street_address = " ".join(addr[:-1])
    city = addr[-1].split(",")[0].strip()
    state = addr[-1].split(",")[1].strip().split(" ")[0].strip()
    zip_postal = addr[-1].split(",")[1].strip().split(" ")[-1].strip()
    country_code = "US"
    latitude = link.select_one('input[name="location-lat"]').get("value")
    longitude = link.select_one('input[name="location-lng"]').get("value")
    if latitude is None:
        latitude = SgRecord.MISSING
    if longitude is None:
        longitude = SgRecord.MISSING
    sgw.write_row(
        SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )
    )


def fetch_data(sgw: SgWriter):
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=headers).text, "html.parser")
        links = soup.select("div#hospitals ul li")
        location_type = "hospital"
        for link in links:
            find_details(link, location_type, session, sgw)

        links = soup.select("div#minormedicalcenters ul li")
        location_type = "medical centers"
        for link in links:
            find_details(link, location_type, session, sgw)

        links = soup.select("div#clinics ul li")
        location_type = "clinics"
        for link in links:
            find_details(link, location_type, session, sgw)

        links = soup.select("div#specialtyfacilities ul li")
        location_type = "specialty facilities"
        for link in links:
            find_details(link, location_type, session, sgw)


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.PHONE, SgRecord.Headers.STREET_ADDRESS},
                fail_on_empty_id=True,
            )
        )
    ) as writer:
        fetch_data(writer)


scrape()
