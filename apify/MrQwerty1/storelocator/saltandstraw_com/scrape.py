import re
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

    return street_address, city, state


def get_additional(page_url):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = " ".join(tree.xpath("//div[@class='shg-row']//text()"))
    try:
        postal = re.findall(r"\w{2} (\d{5})", text).pop()
    except IndexError:
        postal = SgRecord.MISSING

    out = {
        "lat": "".join(tree.xpath("//div[@data-latitude]/@data-latitude")),
        "lng": "".join(tree.xpath("//div[@data-longitude]/@data-longitude")),
        "zip": postal,
    }

    return out


def fetch_data(sgw: SgWriter):
    api = "https://saltandstraw.com/pages/locations"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='division-block' and ./h2]")
    done = set()

    for d in divs:
        slug = "".join(d.xpath("./a[contains(text(), 'MORE')]/@href"))
        if slug in done:
            continue

        done.add(slug)
        location_name = "".join(d.xpath("./h2/text()")).strip()
        line = d.xpath("./div/p/text()")
        line = list(filter(None, [li.strip() for li in line]))
        adr = ", ".join(line)
        street_address, city, state = get_address(adr)
        hours = d.xpath(".//p/strong/text()")
        hours = list(filter(None, [h.replace("OPEN", "Daily").strip() for h in hours]))
        hours_of_operation = ";".join(hours)
        phone = "".join(d.xpath(".//p/em/text()")).strip()
        if slug.startswith("/"):
            page_url = f"https://saltandstraw.com{slug}"
        else:
            page_url = slug
        store_number = "".join(
            d.xpath(".//a[contains(@href, 'locations')]/@href")
        ).split("/")[-1]

        ad = get_additional(page_url)
        postal = ad.get("zip")
        latitude = ad.get("lat")
        longitude = ad.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            store_number=store_number,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://saltandstraw.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
