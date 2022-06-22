from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_api():
    api = "https://www.cropp.com/pl/pl/ajx/stores/all"
    r = session.get(api, headers=headers)
    slug = r.json()["content"]["kml_url"]
    url = f"https:{slug}".replace("_pl", "", 1)

    return url


def fetch_data(sgw: SgWriter):
    m = SgRecord.MISSING
    api = get_api()
    r = session.get(api, headers=headers)
    text = r.text.replace("<![CDATA[", "").replace("]]>", "").encode()
    tree = html.fromstring(text)
    divs = tree.xpath("//placemark")

    for d in divs:
        line = d.xpath(".//description//text()")
        line = list(filter(None, [li.strip() for li in line]))
        hours_of_operation = ";".join(line[line.index("ONA ON") + 1 :])
        line = line[: line.index("ONA ON")]
        phone = line.pop().lower().replace("tel.", "").strip()
        if "доб" in phone:
            phone = phone.split("доб")[0].strip()
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        if not line:
            street_address, city, country_code = m, m, m
        else:
            street_address, city, country_code = line

        store_number = "".join(d.xpath("./@id"))
        location_name = "".join(d.xpath("./name/text()")).strip()
        latitude, longitude = "".join(d.xpath(".//coordinates/text()")).split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.cropp.com/"
    page_url = "https://www.cropp.com/pl/pl/storelocator?show=all"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
