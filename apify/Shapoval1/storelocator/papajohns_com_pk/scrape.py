import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.papajohns.com.pk"
    api_url = "https://www.papajohns.com.pk/restaurants"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="restaurant-summary"]')
    for d in div:

        page_url = "https://www.papajohns.com.pk/restaurants"
        location_name = (
            "".join(d.xpath('.//h3[@class="restaurant-summary__name"]/text()'))
            .replace("\n", "")
            .strip()
        )

        street_address = (
            "".join(d.xpath('.//div[@class="restaurant-summary__address"]/text()'))
            .replace("\n", "")
            .strip()
        )
        cp = (
            "".join(d.xpath('.//div[@class="restaurant-summary__city"]/text()'))
            .replace("\n", "")
            .strip()
        )

        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "PK"
        city = cp
        if cp[0].isdigit():
            postal = cp.split()[0].strip()
            city = " ".join(cp.split()[1:])
        if city.find("Lahore") != -1:
            city = city.split()[-1].strip()
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "<MISSING>"
        jsblock = (
            "".join(tree.xpath('//script[contains(text(), "var shops =")]/text()'))
            .split("var shops =")[1]
            .strip()
        )
        js = json.loads(jsblock)
        for j in js:
            info = j.get("restaurant_info")
            if info.find(f"{location_name}") != -1:
                latitude = j.get("location").get("lat")
                a = html.fromstring(info)
                phone = (
                    "".join(
                        a.xpath(
                            '//a[text()="Order online"]/preceding-sibling::text()[2]'
                        )
                    )
                    .replace("\n", "")
                    .strip()
                )
                longitude = j.get("location").get("lng")
        hours_of_operation = (
            "".join(d.xpath('.//div[@class="restaurant-summary__times"]/p//text()'))
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
