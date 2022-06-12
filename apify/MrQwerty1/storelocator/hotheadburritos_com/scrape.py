from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def get_geo():
    out = dict()
    r = session.get(
        "https://hotheadburritos.com/locationfeed/locations-map/locations-map.php",
        headers=headers,
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")
    for m in markers:
        lat = "".join(m.xpath("./@lat"))
        lng = "".join(m.xpath("./@lng"))
        _id = "".join(m.xpath("./@id")).lower().replace("-", "")
        out[_id] = {"lat": lat, "lng": lng}

    return out


def get_hoo(_id):
    data = {"id": _id}
    r = session.post(
        "https://hotheadburritos.com/locationfeed/locations-landing/landing.php",
        headers=headers,
        data=data,
    )

    tree = html.fromstring(r.text)
    _tmp = []
    for i in range(7):
        hour = "".join(tree.xpath(f"//p[contains(@class, 'd{i}')]/text()")).strip()
        if hour:
            _tmp.append(hour)

    return ";".join(_tmp)


def get_id(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//div[@id='storelanding']/div/@id"))


def fetch_data(sgw: SgWriter):
    api = "https://hotheadburritos.com/locationfeed/getlocations.php"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-data']")
    geo = get_geo()

    for d in divs:
        location_name = "".join(d.xpath(".//a/h3/text()")).strip()
        if "Soon" in location_name:
            continue

        line = d.xpath(".//a/h4/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"

        page_url = "".join(d.xpath(".//a[contains(text(), 'Information')]/@href"))
        if not page_url:
            page_url = f"https://hotheadburritos.com/{city}-{state}".replace(
                " ", "-"
            ).lower()

        store_number = get_id(page_url)
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        try:
            latitude = geo[store_number]["lat"]
            longitude = geo[store_number]["lng"]
        except KeyError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = get_hoo(store_number)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://hotheadburritos.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
