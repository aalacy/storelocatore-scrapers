from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.nl/"
    api_url = (
        "https://www.burgerking.nl/getgeopoints?filter=&restrictToCountry=1&country=nl"
    )
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        store_number = j.get("storeId")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        r = session.get(
            f"https://www.burgerking.nl/getstorebubbleinfo?storeId={store_number}",
            headers=headers,
        )
        js = r.json()
        a = html.fromstring(js)
        slug = "".join(a.xpath("//a/@href"))
        page_url = f"https://www.burgerking.nl{slug}"
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(tree.xpath('//h2[@class="map-heading"]/text()')) or "<MISSING>"
        )
        ad = (
            " ".join(
                tree.xpath(
                    '//td[./span[@class="adress"]]/following-sibling::td[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())

        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = location_name
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "NL"
        city = a.city or "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    '//td[./span[@class="tel"]]/following-sibling::td[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[contains(@class, "col-lg-3 col-md-4")]/div[@class="store-openingtimes square"]//table[@class="openingtimes"]//tr//td//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())
        if str(store_number).find("X") != -1:
            store_number = "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
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
    with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.PAGE_URL}))) as writer:
        fetch_data(writer)
