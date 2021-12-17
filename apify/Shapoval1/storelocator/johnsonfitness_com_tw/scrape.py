import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.johnsonfitness.com.tw/"
    for i in range(0, 20):
        page_url = (
            f"https://www.johnsonfitness.com.tw/mod/store/index.php?y&pos=1&pn={i}"
        )
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        div = tree.xpath('//ul[@class="list"]/li')
        for d in div:

            location_name = "".join(d.xpath('.//div[@class="name"]/text()'))
            ad = (
                "".join(d.xpath('.//div[@class="info"]/div[@class="data"][1]/text()'))
                .split("/")[0]
                .split("：")[1]
                .strip()
            )
            a = parse_address(International_Parser(), ad)
            street_address = (
                f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
                or "<MISSING>"
            )
            if street_address == "<MISSING>" or street_address.isdigit():
                street_address = ad
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "TW"
            city = a.city or "<MISSING>"
            js = (
                "".join(tree.xpath('//script[contains(text(), "var MapInfo")]/text()'))
                .split("var MapInfo = ")[1]
                .split(";")[0]
                .strip()
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            j = json.loads(js)
            for a in j:
                adr = a.get("Address")
                if adr == ad:
                    latitude = a.get("Lat")
                    longitude = a.get("Lng")
            try:
                phone = (
                    "".join(
                        d.xpath('.//div[@class="info"]/div[@class="data"][1]/text()')
                    )
                    .split("/")[1]
                    .split("：")[1]
                    .strip()
                )
            except IndexError:
                phone = "<MISSING>"
            if phone.find("#") != -1:
                phone = phone.split("#")[0].strip()
            hours_of_operation = (
                "".join(d.xpath('.//div[@class="info"]/div[@class="data"][2]/text()'))
                .replace("\n", "")
                .replace("營業時間：", "")
                .strip()
            )

            row = SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=ad,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
