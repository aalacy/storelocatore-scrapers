import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests()

    domain = "accor.com"
    start_url = "https://mercure.accor.com/gb/country/hotels-united-kingdom-pgb.shtml"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_elems = []
    all_locations = dom.xpath('//script[@id="paginator-ids-core"]/text()')[0][
        1:-1
    ].split(",")
    all_locations = [e[1:-1] for e in all_locations]
    for loc in all_locations:
        elem = {"meta.id": {"$eq": loc}}
        all_elems.append(elem)

    for chunk in [all_elems[i : i + 10] for i in range(0, len(all_elems), 10)]:
        api_url = 'https://liveapi.yext.com/v2/accounts/1624327134898036854/entities?api_key=f60a800cdb7af0904b988d834ffeb221&v=20160822&filter={"$or":%s}&languages=en_GB'
        api_url = api_url % str(chunk)
        data = session.get(api_url).json()
        for e in data["response"]["entities"]:
            response = session.get(e["c_pageDestinationURL"])
            dom = etree.HTML(response.text)
            all_locations = dom.xpath(
                '//div[@class="Paginator-listItem"]//a[@class="Teaser-link"]/@href'
            )
            for store_url in all_locations:
                loc_response = session.get(store_url)
                loc_dom = etree.HTML(loc_response.text)
                poi = loc_dom.xpath(
                    '//script[@type="application/ld+json" and contains(text(), "telephone")]/text()'
                )
                if not poi:
                    continue
                poi = json.loads(poi[0])

                street_address = loc_dom.xpath(
                    '//meta[@property="og:street-address"]/@content'
                )[0]
                latitude = loc_dom.xpath('//meta[@property="og:latitude"]/@content')[0]
                longitude = loc_dom.xpath('//meta[@property="og:longitude"]/@content')[
                    0
                ]

                item = SgRecord(
                    locator_domain=domain,
                    page_url=store_url,
                    location_name=poi["name"],
                    street_address=street_address,
                    city=poi["address"]["addressLocality"],
                    state=SgRecord.MISSING,
                    zip_postal=poi["address"]["postalCode"],
                    country_code=poi["address"]["addressCountry"],
                    store_number=SgRecord.MISSING,
                    phone=poi["telephone"],
                    location_type=poi["@type"],
                    latitude=latitude,
                    longitude=longitude,
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
