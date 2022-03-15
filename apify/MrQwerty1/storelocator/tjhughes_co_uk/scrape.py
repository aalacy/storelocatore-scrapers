from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api_url = "https://www.tjhughes.co.uk/map"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0"
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(),' function initialize() {')]/text()")
    )
    text_list = text.split("_marker_latlng =")[1:]

    for t in text_list:
        source = (
            t.split("_content = ")[1].split("';")[0].replace("'", "").replace("+", "")
        )
        root = html.fromstring(source)

        location_name = "".join(root.xpath("./strong/text()")).strip()
        street_address = (
            ", ".join(root.xpath("//span[contains(@class, 'branch-address')]/text()"))
            .replace("TJ Hughes,", "")
            .strip()
        )
        city = "".join(
            root.xpath("//span[contains(@class, 'branch-city')]/text()")
        ).strip()
        postal = "".join(
            root.xpath("//span[contains(@class, 'branch-postcode')]/text()")
        ).strip()
        country_code = "GB"
        phone = (
            "".join(root.xpath("//span[@class='branch-telephone']/text()"))
            .replace("Tel:", "")
            .strip()
        )

        d = tree.xpath(
            f"//div[contains(@class, 'store-locator__store ') and .//*[contains(@href, '{phone.replace(' ', '')}')]]"
        )[0]
        page_url = "https://www.tjhughes.co.uk" + "".join(
            d.xpath(".//a[@class='store-locator__store__link button']/@href")
        )
        store_number = page_url.split("/")[-1]
        latitude, longitude = eval(t.split("LatLng")[1].split(";")[0])
        hours_of_operation = (
            ";".join(d.xpath(".//p[@class='MsoNormal']/text()")[:7]) or "<MISSING>"
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.tjhughes.co.uk/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
