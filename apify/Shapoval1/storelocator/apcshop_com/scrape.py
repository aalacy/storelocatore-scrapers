import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.apcshop.com"
    api_url = "https://www.apcshop.com/retailer/retailer/index/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://www.apcshop.com/retailer/retailer/index/",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = (
        "".join(
            tree.xpath(
                '//script[contains(text(), "window.retailerLocatorConfig")]/text()'
            )
        )
        .split("retailerLocatorData   = ")[1]
        .split("window.retailerLocatorConfig")[0]
        .strip()
    )
    div = "".join(div[:-1])
    js = json.loads(div)
    for j in js["retailers"]:
        url_key = j.get("url_key")
        page_url = (
            f"https://www.apcshop.com/retailer/presentation/retailer/urlKey/{url_key}"
        )
        if (
            page_url
            == "https://www.apcshop.com/retailer/presentation/retailer/urlKey/None"
        ):
            page_url = "https://www.apcshop.com/retailer/retailer/index/"
        if url_key == "https://minishopmadrid.com/":
            page_url = url_key
        location_name = j.get("name") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        street_address = str(street_address).replace(";", "").strip()
        state = "<MISSING>"
        postal = j.get("zip_code") or "<MISSING>"
        if street_address.find(f"{postal}") != -1:
            street_address = street_address.split(f"{postal}")[0].strip()
        country_code = j.get("country")
        city = j.get("city") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = (
            str(j.get("phone_number")).replace("None", "").replace("Femme", "").strip()
            or "<MISSING>"
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        hours_of_operation = "<MISSING>"
        store_number = j.get("code")

        if (
            page_url != "https://www.apcshop.com/retailer/retailer/index/"
            or page_url != "https://minishopmadrid.com/"
        ):
            r = session.get(page_url, headers=headers)
            tree = html.fromstring(r.text)

            hours_of_operation = (
                " ".join(tree.xpath('//tr[@class="schedule"]//text()'))
                .replace("\n", "")
                .strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STORE_NUMBER}))
    ) as writer:
        fetch_data(writer)
