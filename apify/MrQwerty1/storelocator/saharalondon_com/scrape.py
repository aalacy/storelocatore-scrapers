import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    params = []
    r = session.get("https://www.saharalondon.com/locations")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var mapPlugin')]/text()"))
    text = text.split("mapPlugin.addMarkers(")[1].split(");mapPlugin")[0]
    js = json.loads(text)
    for j in js:
        slug = j.get("link")
        lat = j.get("lat") or SgRecord.MISSING
        lng = j.get("lng") or SgRecord.MISSING
        params.append((slug, (lat, lng)))

    return params


def get_data(param: tuple, sgw: SgWriter):
    slug = param[0]
    latitude, longitude = param[1]
    page_url = f"https://www.saharalondon.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = "".join(
        tree.xpath(
            "//p[@class='locations--detail__content__text__address__data__content']/text()"
        )
    ).split("\t")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line.pop(0)
    city = line.pop(0)
    postal = line.pop(0)
    phone = (
        "".join(
            tree.xpath(
                "//p[@class='locations--detail__content__text__address__extra-data__phone']/text()"
            )
        )
        .replace("Tel:", "")
        .strip()
    )

    _tmp = []
    hours = tree.xpath("//tr[@itemprop='openingHours']")
    for h in hours:
        day = "".join(h.xpath("./th/text()")).strip()
        inter = "".join(h.xpath("./td//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        latitude=latitude,
        longitude=longitude,
        country_code="GB",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.saharalondon.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
