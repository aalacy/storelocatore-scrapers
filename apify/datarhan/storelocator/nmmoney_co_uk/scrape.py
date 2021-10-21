# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_url = "https://www.nmmoney.co.uk/branches/GetBranches/51.5073509/-0.1277583?Latitude=51.5073509&longitude=-0.1277583"
    domain = "nmmoney.co.uk"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    all_locations = session.get(start_url, headers=hdr).json()
    for poi in all_locations:
        page_url = (
            f'https://www.nmmoney.co.uk/branches/{poi["SEOBranchNameLink"].lower()}'
        )
        loc_response = session.get(page_url)
        loc_dom = etree.HTML(loc_response.text)
        hoo = loc_dom.xpath('//ul[@id="openeningtime"]//text()')
        hoo = " ".join([e.strip() for e in hoo if e.strip()])
        street_address = poi["AddressLine1"]
        city = poi["AddressLine2"]
        if poi["AddressLine3"]:
            street_address += ", " + poi["AddressLine2"]
            city = poi["AddressLine3"]
        street_address = (
            street_address.replace("&#39;", "'")
            .replace("&#44;", "")
            .replace("&#45;", " ")
        )

        item = SgRecord(
            locator_domain=domain,
            page_url=page_url,
            location_name=poi["BranchName"],
            street_address=street_address,
            city=city.replace("&#39;", "'").replace("&#44;", "").replace("&#45;", " "),
            state="",
            zip_postal=poi["Postcode"],
            country_code="",
            store_number=poi["BranchId"],
            phone=poi["TelephoneNo"],
            location_type=poi["BranchType"],
            latitude=poi["Latitude"],
            longitude=poi["Longitude"],
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
