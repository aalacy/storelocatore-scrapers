from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()
    domain = "thedaileymethod.com"
    start_url = "https://thedaileymethod.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"

    data = session.get(start_url).json()
    response = session.get("https://thedaileymethod.com/locations/")
    dom = etree.HTML(response.text)

    for poi in data["markers"]:
        page_url = poi["link"]
        orig_url = dom.xpath(
            '//a[contains(text(), "%s")]/@href'
            % poi["title"].replace("Dailey Method ", "")
        )
        if orig_url:
            page_url = orig_url[0]
        phone = ""
        zip_code = ""
        raw_address = poi["address"]
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        zip_code = addr.postcode
        if "thedaileymethod" in page_url:
            loc_response = session.get(page_url)
            if loc_response.status_code == 200:
                loc_dom = etree.HTML(loc_response.text)
                if loc_dom.xpath('//div[@id="test"]'):
                    continue
                raw_data = loc_dom.xpath('//div[@id="studio-address"]//text()')
                raw_data = [
                    e.strip() for e in raw_data if e.strip() and "We ask" not in e
                ]
                phone = [e.split("Phone:")[1] for e in raw_data if "Phone" in e]
                phone = phone[0] if phone else ""
                zip_code = raw_data[1].split()[-1]
                cp = [e.split("C.P.")[-1] for e in raw_data if "C.P." in e]
                if cp:
                    zip_code = cp[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=zip_code,
            country_code=addr.country,
            store_number="",
            phone=phone,
            location_type="",
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation="",
            raw_address=raw_address,
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
