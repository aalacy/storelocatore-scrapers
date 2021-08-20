# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = (
        "https://storerocket.io/api/user/56wpZ22pAn/locations?radius=50&units=miles"
    )
    domain = "slimchickens.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    data = session.get(start_url, headers=hdr).json()

    all_locations = data["results"]["locations"]
    for poi in all_locations:
        page_url = f'https://slimchickens.com/location/{poi["slug"]}'
        if "coming-soon" in page_url:
            continue
        loc_response = session.get(page_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)
        if loc_dom.xpath('//h1[contains(text(), "Coming Soon")]'):
            continue

        street_address = poi["address_line_1"]
        if poi["address_line_2"]:
            street_address += " " + poi["address_line_2"]
        phone = [e for e in poi["fields"] if e["name"] == "Phone"]
        phone = phone[0]["pivot_field_value"] if phone else SgRecord.MISSING
        hours_of_operation = [e for e in poi["fields"] if e["name"] == "Hours"]
        hours_of_operation = (
            hours_of_operation[0]["pivot_field_value"].replace("</br>", " ")
            if hours_of_operation
            else SgRecord.MISSING
        )
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["postcode"]
        if not street_address:
            addr = parse_address_intl(poi["address"])
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += " " + addr.street_address_2
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
        if not street_address:
            addr = parse_address_intl(loc_dom.xpath("//h1/text()")[0])
            city = addr.city
            state = addr.state
            zip_code = addr.postcode
        if loc_response.status_code == 200:
            street_address = loc_dom.xpath("//h1/text()")[0].split(",")
            if len(street_address) == 5:
                street_address = ", ".join(street_address[:2])
            else:
                street_address = street_address[0]

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["name"],
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_code,
            country_code=poi["country"],
            store_number=poi["id"],
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lng"],
            hours_of_operation=hours_of_operation,
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
