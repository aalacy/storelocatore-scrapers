import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://gulfsverige.com/hitta-station/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'markers_attrs_array.push')]/text()")
    )
    text = text.split("eval(")[1].split("]]),")[0].replace("false", "False") + "]]"
    arr = eval(text)

    for ar in arr:
        store_number = ar[1]
        latitude = ar[2]
        longitude = ar[3]
        location_name = ar[7]
        source = ar[-1]
        d = html.fromstring(source)
        raw_address = "".join(
            d.xpath(".//span[@itemprop='streetAddress']/text()")
        ).strip()
        if raw_address.endswith(","):
            raw_address = raw_address[:-1]

        try:
            postal = re.findall(r"(\d{3} \d{2}|\d{5})", raw_address)[0]
        except IndexError:
            postal = SgRecord.MISSING

        if postal == SgRecord.MISSING:
            street_address = raw_address
            city = SgRecord.MISSING
        else:
            street_address = raw_address.split(postal)[0].strip()
            city = raw_address.split(postal)[-1].strip()

        if street_address.endswith(","):
            street_address = street_address[:-1]
        country_code = "SE"
        page_url = f"https://gulfsverige.com/hitta-station/#w2mb-listing-{store_number}"
        phone = "".join(d.xpath(".//meta[@itemprop='telephone']/@content"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://gulfsverige.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
