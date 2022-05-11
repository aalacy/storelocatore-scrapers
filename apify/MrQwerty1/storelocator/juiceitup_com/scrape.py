import json5
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    adr1 = a.get("address1") or ""
    adr2 = a.get("address2") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.juiceitup.com/locations/"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='loc_info']")

    coords = dict()
    text = "".join(tree.xpath("//script[contains(text(), 'var locPins')]/text()"))
    text = "[" + text.split("locPins.push(")[1].split(");")[0] + "]"
    js = json5.loads(text)
    for j in js:
        url = j.get("perma") or ""
        key = url.split("/")[-2]
        lat = j.get("lat")
        lng = j.get("lng")
        coords[key] = (lat, lng)

    for d in divs:
        location_name = "".join(d.xpath(".//h2/a/text()")).strip()
        page_url = "".join(d.xpath(".//h2/a/@href"))

        if d.xpath(".//div[@class='coming_soon']"):
            continue

        line = d.xpath(".//div[@class='full_add info_txt info_icon icon_pin']/a/text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        phone = "".join(
            d.xpath(".//div[@class='phone info_txt info_icon icon_phone']//text()")
        ).strip()

        key = page_url.split("/")[-2]
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        source = "".join(d.xpath(".//div[@class='hrs_status']/@data-hours")) or "{}"
        hours = json5.loads(source)

        i = 0
        for day in days:
            if isinstance(hours, dict):
                v = hours.get(str(i))
                if not v:
                    _tmp.append(f"{day}: Closed")
                    i += 1
                    continue
            else:
                try:
                    v = hours[i]
                except IndexError:
                    _tmp.append(f"{day}: Closed")
                    i += 1
                    continue

            start = v.get("open")
            end = v.get("close")
            _tmp.append(f"{day}: {start}-{end}")
            i += 1

        hours_of_operation = ";".join(_tmp)

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
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.juiceitup.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
