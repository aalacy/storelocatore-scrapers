import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://australianice.com/locations/?lang=en"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@data-lng]")

    for d in divs:
        raw_address = " ".join(
            " ".join(d.xpath(".//div[@class='premium-maps-info-desc']//text()")).split()
        ).replace("2 000", "2000")
        postal = re.findall(r"\d{4}", raw_address).pop()
        street_address, city = raw_address.split(postal)
        city = city.replace("–", "").strip()
        street_address = street_address.replace("NL-", "").strip()
        country_code = "BE"
        if "Nederland" in city:
            city = city.replace("Nederland", "").replace("CV", "").strip()
            country_code = "NL"
        location_name = "".join(
            d.xpath(".//p[@class='premium-maps-info-title']/text()")
        ).strip()
        page_url = d.xpath(".//a/@href")[0]
        latitude = "".join(d.xpath("./@data-lat"))
        longitude = "".join(d.xpath("./@data-lng"))

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://australianice.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
