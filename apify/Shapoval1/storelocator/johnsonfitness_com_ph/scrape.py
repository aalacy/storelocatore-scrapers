from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://johnsonfitness.com.ph"
    api_url = "https://johnsonfitness.com.ph/pages/stores"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="map__store-item"]')
    for d in div:

        page_url = "https://johnsonfitness.com.ph/pages/stores"
        location_name = "".join(d.xpath(".//button/text()")).replace("\n", "").strip()
        ad = (
            " ".join(d.xpath('.//div[@class="map__store-address rte"]/p/text()'))
            .replace("\n", "")
            .split("09")[0]
            .strip()
        )
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "PH"
        city = a.city or "<MISSING>"
        phone_list = d.xpath('.//div[@class="map__store-address rte"]/p/text()')
        phone_list = list(filter(None, [a.strip() for a in phone_list]))

        tmp = []
        for p in phone_list:
            if "09" in p:
                tmp.append(p)
                break
        phone = "".join(tmp)
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="map__store-hours rte"]/p/text()'))
            .replace("\n", "")
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
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
