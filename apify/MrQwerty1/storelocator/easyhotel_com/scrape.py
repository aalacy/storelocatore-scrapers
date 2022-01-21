import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_phone(source):
    tree = html.fromstring(source)
    phone = "".join(tree.xpath("//p[contains(text(), 'TEL:')]/text()"))
    phone = phone.replace("TEL:", "").strip()

    return phone


def fetch_data(sgw: SgWriter):
    api = "https://www.easyhotel.com/hotels"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'window.__REACT__STATE__=')]/text()")
    )
    text = text.split("window.__REACT__STATE__=")[1].split("}};")[0] + "}}"
    js = json.loads(text)["hotels"]["hotelsById"].values()

    for j in js:
        location_name = j.get("name")
        slug = j.get("url")
        page_url = f"https://www.easyhotel.com/hotels{slug}"
        street_address = j.get("street") or ""
        street_address = street_address.replace("\n", "").replace("\r", "")
        city = j.get("city")
        postal = j.get("postcode")
        country = j.get("country")

        phone = j.get("phone") or get_phone(j["sections"]["contactDetails"])
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        store_number = j.get("hotelCode")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.easyhotel.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
