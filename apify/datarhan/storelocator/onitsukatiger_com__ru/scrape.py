from w3lib.url import add_or_replace_parameter
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    start_urls = [
        "https://www.onitsukatiger.com/ru/ru-ru/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/id/en-id/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/ph/en-ph/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/in/en-in/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/jp/ja-jp/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/hk/en-hk/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/cn/zh-cn/store-finder.json?default=y&page=1",
        "https://www.onitsukatiger.com/za/en-za/store-finder.json?default=y&page=1",
    ]

    domain = "onitsukatiger.com/ru"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for url in start_urls:
        data = session.get(url, headers=hdr).json()
        all_locations = data["Stores"]
        while data["HasNext"]:
            data = session.get(
                add_or_replace_parameter(url, "page", data["Next"]), headers=hdr
            ).json()
            all_locations.update(data["Stores"])

        for i, poi in all_locations.items():
            page_url = "https://www.onitsukatiger.com" + poi["URL"]
            loc_response = session.get(page_url)
            loc_dom = etree.HTML(loc_response.text)

            hoo = loc_dom.xpath(
                '//table[@class="store-openings weekday_openings"]//text()'
            )
            hoo = hoo = [e.strip() for e in hoo if e.strip()]
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url=page_url,
                location_name=poi["Title"],
                street_address=poi["Address"],
                city=poi["City"],
                state=poi["Region"],
                zip_postal=poi["Postcode"],
                country_code=poi["Country"],
                store_number="",
                phone=poi["Phone"],
                location_type=poi["StoreType"],
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
