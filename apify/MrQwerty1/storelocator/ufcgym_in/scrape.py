import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_additional(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//a[contains(@href, 'map')]/@href"))
    latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]
    hours_of_operation = (
        "".join(
            tree.xpath("//span[contains(text(), 'Hours')]/following-sibling::text()")
        )
        .replace(": ", "")
        .strip()
    )

    return latitude, longitude, hours_of_operation


def fetch_data(sgw: SgWriter):
    api = "https://ufcgym.in/locations.html"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='gym-location' and ./a[contains(@href, '.html')]]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[@class='gym-location__title-primary']/text()")
        ).strip()
        city = location_name.split("-")[-1].strip()
        state = "".join(d.xpath("./preceding-sibling::h2/text()")).strip()
        street_address = d.xpath(".//p[@class='gym-location__gym-address']/text()")[
            0
        ].strip()
        if street_address.endswith(","):
            street_address = street_address[:-1]
        raw_address = " ".join(
            "".join(d.xpath(".//p[@class='gym-location__gym-address']/text()")).split()
        )
        postal = re.findall(r"\d{6}", raw_address).pop()
        country_code = "IN"
        slug = "".join(d.xpath(".//a[@class='button gym-location__cta']/@href"))
        page_url = f"https://ufcgym.in{slug}"
        phone = d.xpath(".//a[@class='gym-location__gym-phone']/text()")[0].strip()
        latitude, longitude, hours_of_operation = get_additional(page_url)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://ufcgym.in/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
