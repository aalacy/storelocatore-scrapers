from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    url = "https://www.kingofdonair.ca/order-online-choose-a-location/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    divlist = soup.find("ul", {"id": "locations"}).findAll("li")
    for div in divlist:
        title = div.find("h2").text
        address = div.find("a").text
        try:
            lat, longt = (
                div.find("a")["href"].split("@", 1)[1].split("data", 1)[0].split(",", 1)
            )
            longt = longt.split(",", 1)[0]
        except:
            lat = longt = "<MISSING>"
        phone = div.find("a", {"class": "telNumber"}).text
        try:
            street, city, state = address.split(", ")
        except:
            street, temp, city, state = address.split(", ")
            street = street + " " + temp
        yield SgRecord(
            locator_domain="https://www.kingofdonair.ca/",
            page_url=SgRecord.MISSING,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=SgRecord.MISSING,
            country_code="CA",
            store_number=SgRecord.MISSING,
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
