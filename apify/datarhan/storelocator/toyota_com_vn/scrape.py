from lxml import etree

from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl


def fetch_data():
    session = SgRequests(verify_ssl=False)

    start_url = "https://www.toyota.com.vn/api/common/provinces"
    domain = "toyota.com.vn"
    hdr = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,ru-RU;q=0.8,ru;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://www.toyota.com.vn/danh-sach-dai-ly",
        "Cookie": "D1N=b15bfa3c0d478cf87e79df558cd7e331",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session.get("https://www.toyota.com.vn/danh-sach-dai-ly")
    data = session.get(start_url, headers=hdr).json()
    for p in data["Data_Ext"]["result"]["items"]:
        url = f'https://www.toyota.com.vn/api/common/dealerbyprovinceidanddistrictid?provinceId={p["code"]}&districtId='
        data = session.get(url, headers=hdr).json()

        for poi in data["Data_Ext"]["result"]:
            raw_address = poi["address"]
            addr = parse_address_intl(raw_address)
            street_address = addr.street_address_1
            if addr.street_address_2:
                street_address += ", " + addr.street_address_2
            geo = ["", ""]
            if poi["mapUrl"]:
                geo = (
                    etree.HTML(poi["mapUrl"].replace('""', '"'))
                    .xpath("//@src")[0]
                    .split("!2d")[-1]
                    .split("!2m")[0]
                    .split("!3d")
                )

            item = SgRecord(
                locator_domain=domain,
                page_url="https://www.toyota.com.vn/danh-sach-dai-ly",
                location_name=poi["name"],
                street_address=street_address,
                city=addr.city,
                state=poi["province"],
                zip_postal=addr.postcode,
                country_code="VN",
                store_number=poi["code"],
                phone=poi["phone"],
                location_type="",
                latitude=geo[0],
                longitude=geo[1],
                hours_of_operation=poi["operatingTime"],
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
