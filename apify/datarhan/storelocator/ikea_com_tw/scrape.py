from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests()

    start_url = "https://www.ikea.com.tw/zh/store/index/"
    domain = "ikea.com.tw"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//strong/a[contains(@href, "/store/")]/@href')
    for url in all_locations:
        url = url.replace("/zh/", "/en/").replace("/store/", "/en/store/")
        page_url = urljoin(start_url, url).replace("index", "info")
        loc_response = session.get(page_url)
        if loc_response.status_code != 200:
            page_url = urljoin(start_url, url)
            loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = (
            loc_dom.xpath("//h1/text()")[0]
            .split("opening hours")[0]
            .split("｜")[0]
            .split("Opening")[0]
            .strip()
        )
        if "Pick-up and Order Point" in location_name:
            continue
        if "Mobile Shop" in location_name:
            continue
        hoo = loc_dom.xpath(
            '//span[descendant::span[contains(text(), "Opening hours:")]]/following-sibling::span//text()'
        )
        if not hoo:
            hoo = loc_dom.xpath(
                '//h5[descendant::span[contains(text(), "-Store")]]/following-sibling::span[1]//text()'
            )
        if not hoo:
            hoo = loc_dom.xpath('//div[contains(text(), "Opening hours")]/text()')
            hoo = [hoo[0].split("：")[-1]] if hoo else []
        if not hoo:
            hoo = loc_dom.xpath(
                '//strong[contains(text(), "Store opens daily")]/following-sibling::strong/text()'
            )[:1]
        if not hoo:
            hoo = loc_dom.xpath('//div[strong[contains(text(), "IKEA Shop")]]/text()')[
                :2
            ]
        if not hoo:
            hoo = loc_dom.xpath('//h5[contains(text(), "Store")]/following::text()')[:1]
        if not hoo:
            hoo = loc_dom.xpath('//span[contains(text(), "Monday~Sunday")]/text()')[:1]
        hoo = [e.strip() for e in hoo if e.strip()]
        hoo = " ".join(hoo).split("🍴")[0].strip()
        raw_data = loc_dom.xpath(
            '//span[@style="font-family:Calibri,sans-serif" and span[span[contains(text(), "Address")]]]//text()'
        )
        if not raw_data:
            raw_data = loc_dom.xpath('//span[contains(text(), "Address:")]/text()')[:1]
        if not raw_data:
            raw_data = loc_dom.xpath('//div[contains(text(), "Opening hours")]/text()')
            raw_data = [e.strip() for e in raw_data if "Address" in e]
        if not raw_data:
            raw_data = loc_dom.xpath('//p[contains(text(), "Address：")]/text()')[:1]
        if not raw_data:
            raw_data = loc_dom.xpath("//div[h3]/text()")
            raw_data = [e.strip() for e in raw_data if "Address" in e and e.strip()]
        if not raw_data:
            raw_data = [
                loc_dom.xpath(
                    '//h4[contains(text(), "General information")]/following::text()'
                )[0]
            ]
        raw_data = [e.strip() for e in raw_data]
        raw_address = (
            " ".join(raw_data)
            .split("Address:")[-1]
            .split("Tel:")[0]
            .strip()
            .replace("Address：", "")
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += ", " + addr.street_address_2
        phone = ""
        if "Tel:" in raw_data[-1]:
            phone = raw_data[-1].split("Tel:")[-1].strip()
        if not phone:
            phone = loc_dom.xpath('//span[contains(text(), "Tel.:")]/text()')
            phone = phone[0].split("Tel.:")[-1].strip() if phone else ""
        if not phone:
            phone = loc_dom.xpath("//div[h3]/text()")
            phone = [e.strip() for e in raw_data if "Tel" in e]
            phone = phone[0].split("Tel.:")[-1].strip() if phone else ""
        if not phone:
            phone = loc_dom.xpath('//div[contains(text(), "Opening hours")]/text()')
            phone = [e.strip() for e in phone if "Tel" in e]
            phone = phone[0].split("Tel.:")[-1].strip() if phone else ""
        if not phone:
            phone = loc_dom.xpath('//p[contains(text(), "Address")]/text()')
            phone = [e.strip() for e in phone if "Landline users" in e]
            phone = phone[0].split("users:")[-1].strip() if phone else ""
        if not phone:
            phone = loc_dom.xpath("//div[h3]/text()")
            phone = [e.strip() for e in phone if "Tel" in e]
            phone = phone[0].split("Tel.:")[-1].strip() if phone else ""
        if not phone:
            phone = loc_dom.xpath('//div[h4[contains(text(), "General")]]/text()')
            phone = [e.strip() for e in phone if "service direct line:" in e]
            phone = phone[0].split("direct line:")[-1].strip() if phone else ""
        phone = (
            phone.split("press")[0]
            .split("option")[0]
            .split("#")[0]
            .replace(",", "")
            .strip()
        )
        city = addr.city
        if city and city.endswith("."):
            city = city[:-1]
        city = city.split("District")[-1].replace("City", "").strip()

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state="",
            zip_postal="",
            country_code="TW",
            store_number="",
            phone=phone,
            location_type="",
            latitude="",
            longitude="",
            hours_of_operation=hoo,
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
