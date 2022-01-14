import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_hours(page_url):
    _tmp = []
    r = session.get(page_url)
    if r.status_code == 404:
        return ""
    tree = html.fromstring(r.text)
    tr = tree.xpath("//div[@id='hours']//tr")
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        if "Hours" in time:
            continue
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    coords = []
    phones = dict()
    api = "https://www.gameworks.com/home"

    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(
        tree.xpath("//script[contains(text(), 'var marker =')]/text()")
    ).split("var marker =")[1:]
    for t in text:
        lat = t.split("lat:")[1].split(",")[0].strip()
        lng = t.split("lng:")[1].split("}")[0].strip()
        coords.append((lat, lng))

    js_text = "".join(tree.xpath("//script[contains(text(), 'LocalBusiness')]/text()"))
    js = json.loads(js_text)
    for j in js["address"]:
        key = j.get("postalCode") or ""
        phones[key] = j.get("telephone") or ""

    divs = tree.xpath("//ul[@class='location-map-listing']/li")
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[contains(@class,'location-name')]/a/text()")
        ).strip()
        slug = "".join(d.xpath(".//div[contains(@class,'location-name')]/a/@href"))
        page_url = f"https://www.gameworks.com{slug}"

        line = d.xpath(".//div[contains(@class,'location-address')]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        phone = (
            "".join(d.xpath(".//div[contains(@class,'location-phone')]//text()"))
            .replace(" . ", " ")
            .strip()
        ) or phones.get(postal)
        latitude, longitude = coords.pop(0)
        hours_of_operation = get_hours(page_url)
        if "SOON" in hours_of_operation:
            hours_of_operation = "Coming Soon"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.gameworks.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
