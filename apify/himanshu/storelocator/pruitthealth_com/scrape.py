from lxml import etree
from urllib.parse import urljoin

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_url = "https://www.pruitthealth.com/bin/pruitthealthlocator"
    domain = "pruitthealth.com"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    exclude = [
        "https://www.pruitthealth.com/therapy-services",
        "https://www.pruitthealth.com/consulting",
    ]

    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        store_url = urljoin(start_url, poi["WebsiteUrl"])
        if store_url in exclude:
            continue
        loc_response = session.get(store_url)
        if loc_response.status_code != 200:
            continue
        loc_dom = etree.HTML(loc_response.text)

        phone = SgRecord.MISSING
        if "pruitthealth.com" in store_url:
            phone = loc_dom.xpath('//*[contains(text(), "tel:")]/text()')
            if phone:
                phone = phone[0].split("fax:")[0].replace("tel:", "").strip()
                if not phone:
                    phone = loc_dom.xpath('//b[i[contains(text(), "tel:")]]/text()')
                    if phone:
                        phone = phone[0].strip()
            if not phone:
                phone = loc_dom.xpath('//*[i[contains(text(), "tel:")]]/text()')
                phone = phone[0].strip()
        store_number = poi["Index"]
        if "facilityid" in store_url:
            store_number = store_url.split("facilityid")[-1]

        item = SgRecord(
            locator_domain=domain,
            page_url=store_url,
            location_name=poi["Title"],
            street_address=poi["StreetAddress"],
            city=poi["City"],
            state=poi["State"],
            zip_postal=poi["Zip"],
            country_code=SgRecord.MISSING,
            store_number=store_number,
            phone=phone,
            location_type=poi["ServiceType"],
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
