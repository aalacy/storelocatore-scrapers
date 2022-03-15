# --extra-index-url https://dl.cloudsmith.io/KVaWma76J5VNwrOm/crawl/crawl/python/simple/
import json
from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter


def fetch_data():
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    start_urls = [
        "https://www.yellowmap.de/Presentation/AldiSued/sl-SI/ResultList?callback=jQuery20308425583268940957_1630315540655&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=14.19708251953125&Luy=46.5002829039397&Rlx=15.83953857421875&Rly=45.31546044422575&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIPA=false&Filters.ASxKAFE=false&Filters.ASxFIGS=false&Filters.ASxFIBA=false&Filters.ASxFITF=false&Filters.ASxFIWC=false&_=1630315540660",
        "https://www.yellowmap.de/Presentation/AldiSued/sl-SI/ResultList?callback=jQuery20308425583268940957_1630315540655&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=13.1781005859375&Luy=46.45299704748289&Rlx=14.820556640625&Rly=45.26715476332791&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIPA=false&Filters.ASxKAFE=false&Filters.ASxFIGS=false&Filters.ASxFIBA=false&Filters.ASxFITF=false&Filters.ASxFIWC=false&_=1630315540668",
        "https://www.yellowmap.de/Presentation/AldiSued/sl-SI/ResultList?callback=jQuery20308425583268940957_1630315540655&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=13.875732421875&Luy=46.74927110475196&Rlx=15.5181884765625&Rly=45.569832358492825&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIPA=false&Filters.ASxKAFE=false&Filters.ASxFIGS=false&Filters.ASxFIBA=false&Filters.ASxFITF=false&Filters.ASxFIWC=false&_=1630315540670",
        "https://www.yellowmap.de/Presentation/AldiSued/sl-SI/ResultList?callback=jQuery20308425583268940957_1630315540655&LocX=&LocY=&HiddenBranchCode=&BranchCode=&Lux=14.5184326171875&Luy=47.081344869872034&Rlx=16.160888671875&Rly=45.909122123907295&ZoomLevel=9&Mode=None&Filters.OPEN=false&Filters.ASxFIPA=false&Filters.ASxKAFE=false&Filters.ASxFIGS=false&Filters.ASxFIBA=false&Filters.ASxFITF=false&Filters.ASxFIWC=false&_=1630315540674",
    ]
    domain = "hofer.si"
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    for start_url in start_urls:
        response = session.get(start_url, headers=hdr)
        data = response.text.split("0655(")[-1][:-1]
        data = json.loads(data)
        dom = etree.HTML(data["Container"])

        all_locations = dom.xpath("//li[@data-json]")
        for poi_html in all_locations:
            location_name = poi_html.xpath('.//strong[@itemprop="name"]/text()')[0]
            street_address = poi_html.xpath('.//div[@itemprop="streetAddress"]/text()')[
                0
            ]
            zip_code = poi_html.xpath('.//div[@itemprop="addressLocality"]/text()')[
                0
            ].split()[0]
            city = " ".join(
                poi_html.xpath('.//div[@itemprop="addressLocality"]/text()')[0].split()[
                    1:
                ]
            )
            poi = json.loads(poi_html.xpath("@data-json")[0])
            hoo = []
            for e in poi["openingHours"]:
                hoo.append(f"{e['day']['text']} {e['from']} - {e['until']}")
            hoo = " ".join(hoo)

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.hofer.si/trgovine/",
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=SgRecord.MISSING,
                zip_postal=zip_code,
                country_code=poi["countryCode"].split("-")[-1].upper(),
                store_number=SgRecord.MISSING,
                phone=SgRecord.MISSING,
                location_type=SgRecord.MISSING,
                latitude=poi["locX"],
                longitude=poi["locY"],
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
