import re
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

    start_url = "https://www.hammonds-uk.com/api/token"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")

    session.get("https://www.hammonds-uk.com/find-your-local-showroom")
    response = session.get(start_url)
    token = response.text[1:-1]
    hdr = {
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "x-csrf-token": token,
        "x-requested-with": "XMLHttpRequest",
    }
    frm = {"postcode": "UK", "ranges": ["", "", "", ""]}
    all_locations = session.post(
        "https://www.hammonds-uk.com/api/stores/find", headers=hdr, json=frm
    ).json()

    for poi in all_locations:
        page_url = urljoin(start_url, poi["url"])
        loc_response = session.get(page_url)
        code = loc_response.status_code
        while code != 200:
            session = SgRequests()
            loc_response = session.get(page_url)
            code = loc_response.status_code
        loc_dom = etree.HTML(loc_response.text)
        addr = parse_address_intl(poi["address"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address += " " + addr.street_address_2
        hoo = loc_dom.xpath('//div[@class="store-detail__openinghours medium"]//text()')
        hoo = [e.replace("\n", "").strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(" ".join(hoo).split())

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["title"],
            street_address=street_address,
            city=addr.city,
            state=addr.state,
            zip_postal=addr.postcode,
            country_code=addr.country,
            store_number=SgRecord.MISSING,
            phone=poi["telephone"],
            location_type=SgRecord.MISSING,
            latitude=poi["lat"],
            longitude=poi["lon"],
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
