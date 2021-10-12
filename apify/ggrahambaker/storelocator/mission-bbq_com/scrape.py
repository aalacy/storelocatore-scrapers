# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import re
import demjson
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://mission-bbq.com/locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="esg-entry-content eg-mission-content"]')
    data = re.findall(r"tpessential\((.+?)\);", response.text.replace("\n", ""))[0]
    data = demjson.decode(data)
    all_ids = [str(e[0]) for e in data["loadMoreItems"]]
    frm = {
        "action": "Essential_Grid_Front_request_ajax",
        "client_action": "load_more_items",
        "token": "327636e022",
        "data[]": all_ids,
        "gridid": "1",
    }

    url = "https://mission-bbq.com/wp-admin/admin-ajax.php"
    data = session.post(url, headers=hdr, data=frm).json()
    dom = etree.HTML(data["data"])
    all_locations += dom.xpath('//div[@class="esg-entry-content eg-mission-content"]')
    for poi_html in all_locations:
        raw_data = poi_html.xpath(".//text()")
        raw_data = [e.strip() for e in raw_data if e.strip()]
        addr = parse_address_intl(" ".join(raw_data[1:3]))
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        phone = [e for e in raw_data if "Restaurant" in e][0].split(":")[-1].strip()
        if "Coming Soon" in phone:
            continue

        item = SgRecord(
            locator_domain=domain,
            page_url="https://mission-bbq.com/locations/",
            location_name=raw_data[0],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=poi_html.xpath('.//*[contains(@class, "eg-post-")]/@class')[0]
            .split()[1]
            .split("-")[-1],
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
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
