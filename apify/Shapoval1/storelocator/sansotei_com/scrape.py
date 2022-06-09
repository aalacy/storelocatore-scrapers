from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.sansotei.com/"
    page_url = "https://www.sansotei.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="_1ncY2"] | //div[@class="_2Hij5"]')

    for d in div:

        location_name = (
            "".join(d.xpath('.//span[@style="font-size:30px;"]//text()'))
            .replace("\n", "")
            .strip()
        )
        if not location_name:
            continue

        ad = "".join(
            d.xpath('.//span[@style="font-size:30px;"]/following::a[1]//text()')
        )
        if ad.find("1201") == -1:
            ad = (
                ad
                + " "
                + "".join(
                    d.xpath(
                        './/span[@style="font-size:30px;"]/following::a[1]/following::*[contains(text(), ",")][1]//text()'
                    )
                )
            )
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        country_code = "CA"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath('.//a[contains(@href, "tel")]//text()'))
            .replace("​", "")
            .strip()
            or "<MISSING>"
        )
        if location_name == "UNION STN":
            phone = "".join(
                d.xpath('.//following::a[contains(@href, "tel")][1]//text()')
            )
        if location_name == "ADELAIDE":
            phone = "".join(
                d.xpath('.//preceding::a[contains(@href, "tel")][1]//text()')
            )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/span[@style="font-family:oswald-extralight,oswald,sans-serif;"]//text()'
                )
            )
            .replace("\n", "")
            .replace("​", "")
            .replace("URBAN EATERY LOWEST LEVEL", "")
            .replace("TASTE MRKT UPPER LEVEL", "")
            .strip()
            or "<MISSING>"
        )
        text = "".join(d.xpath('.//a[contains(@href, "/maps")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=SgRecord.MISSING,
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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
