import json
from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.papajohns.ph/"
    api_url = "https://www.papajohns.ph/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath(
        '//div[@class="restaurant-details"]/h3 | //div[@class="restaurant-details__item restaurant-details__item_open"]/div/p[./strong]'
    )

    for b in block:

        page_url = "https://www.papajohns.ph/restaurants"
        ad = (
            " ".join(
                b.xpath(
                    './/following-sibling::div[@class="restaurant-details__item restaurant-details__item_address"]/div/text() | .//following-sibling::p[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        location_name = "".join(b.xpath(".//text()")).replace("\n", "").strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()

        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "PH"
        city = a.city or "<MISSING>"
        if location_name == "Paranaque":
            street_address = "#7 Aguinaldo St. Malacañang Vill"
            city = "Manila"
            postal = "1700"
        if location_name == "CLEAN FUEL GAS STATION Booth":
            street_address = "Quirino Highway Brgy. Bagbag, Novaliches"
            city = "Quezon City"
        if location_name == "Sta Rosa, Laguna":
            street_address = "Balibago, Santa Rosa"
            city = "Santa Rosa"
            postal = "73QV+6R"
        phone = (
            "".join(
                b.xpath(
                    './/following-sibling::div[@class="restaurant-details__item restaurant-details__item_phone"]/div/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                b.xpath(
                    './/following-sibling::div[@class="restaurant-details__item restaurant-details__item_open"]/div/p[1]/text() | .//following::*[contains(text(), "pm")][1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ll = (
            "".join(tree.xpath('//script[contains(text(), "var shops =")]/text()'))
            .split("var shops =")[1]
            .strip()
        )
        js = json.loads(ll)
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        for j in js:
            info = "".join(j.get("restaurant_info")).replace("\r\n", " ").strip()
            if info.find(f"{location_name}") != -1:
                latitude = j.get("location").get("lat")
                longitude = j.get("location").get("lng")

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
