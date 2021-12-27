from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address
from lxml import html


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.mcdonalds.co.jp/"
    api_url = "https://map.mcdonalds.co.jp/api/poi?uuid=c9d0709e-219a-4b92-bff0-661475e10a9c&bounds=30.751277776257805%2C125.15624999999999%2C39.90973623453717%2C144.84375000000003&_=1629401995227"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        key = j.get("key")
        page_url = f"https://map.mcdonalds.co.jp/map/{key}"
        location_name = j.get("name") or "<MISSING>"
        ad = "".join(j.get("address"))
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        country_code = "JP"
        city = a.city or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        postal = (
            "".join(
                tree.xpath(
                    '//span[@class="icon icon-zip"]/following-sibling::span/text()'
                )
            ).strip()
            or "<MISSING>"
        )
        phone = (
            "".join(
                tree.xpath(
                    '//span[@class="icon icon-tel"]/following-sibling::span/a/text()'
                )
            ).strip()
            or "<MISSING>"
        )
        tmp = []
        days = "".join(tree.xpath("//table/tbody/tr/th/text()"))
        times = "".join(tree.xpath("//table/tbody/tr/td[1]/text()"))
        for d, t in zip(days, times):
            tmp.append(f"{d.strip()}: {t.strip()}")
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
