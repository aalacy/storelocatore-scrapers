from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.popeyes.com.tr/Restaurants/GetRestaurants/"
    domain = "popeyes.com.tr"

    all_locations = session.get(start_url).json()
    for poi in all_locations:
        page_url = f"https://www.popeyes.com.tr/subeler/{poi['data']['city'].replace(' ', '-')}/{poi['data']['county'].replace(' ', '-')}/{poi['data']['title'].strip().replace(' ', '-')}"
        page_url = (
            page_url.lower()
            .replace("ü", "u")
            .replace("ğ", "g")
            .replace("ç", "c")
            .replace("ö", "o")
            .replace("ş", "s")
            .replace("ı", "i")
            .replace("i̇", "i")
            .replace("--", "-")
        )
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath(
            '//dt[contains(text(), "Çalışma Saatleri")]/following-sibling::dd/text()'
        )
        hoo = " ".join(hoo).strip()
        if hoo == "-":
            hoo = ""

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["data"]["title"],
            street_address=poi["data"]["address"],
            city=poi["data"]["city"],
            state=poi["data"]["county"],
            zip_postal="",
            country_code="TR",
            store_number="",
            phone=poi["data"]["phone"],
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hoo,
        )

        yield item


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
