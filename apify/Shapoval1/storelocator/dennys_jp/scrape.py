from lxml import html
from sgpostal.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://dennys.jp/"
    api_url = "https://shop.dennys.jp/api/poi?uuid=925c420c-115d-4283-9405-93713571ede7&extra_fields=brand&bounds=35.648369157374255%2C139.669189453125%2C35.71975793933433%2C139.866943359375&zoom=14&_=1630872555682"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        key = j.get("key")
        page_url = f"https://shop.dennys.jp/map/{key}"
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")

        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        postal = "".join(
            tree.xpath('//th[./span[text()="郵便番号"]]/following-sibling::td/text()')
        )
        ad = "".join(
            tree.xpath('//th[.//span[text()="住所"]]/following-sibling::td/text()')
        )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or ad
        )
        if street_address == "<MISSING>":
            street_address = ad
        state = a.state or "<MISSING>"
        city = a.city or "<MISSING>"
        country_code = "JP"
        phone = "".join(
            tree.xpath('//th[./span[text()="電話番号"]]/following-sibling::td//text()')
        )
        hours_of_operation = (
            " ".join(
                tree.xpath('//th[./span[text()="営業時間"]]/following-sibling::td//text()')
            )
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
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
