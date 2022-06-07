import json
import re
import usaddress

from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sglogging import sglog


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

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        adr1 = a.get("address1") or ""
        adr2 = a.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip()
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
    except usaddress.RepeatedLabelError:
        adr = line.split(",")
        state, postal = adr.pop().strip().split()
        city = adr.pop().strip()
        street_address = ",".join(adr)

    return street_address, city, state, postal


def get_additional(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//div[@class='para' and ./a]//text()")
    line = list(filter(None, [li.strip() for li in line]))
    adr = line[: line.index("Phone:")]
    raw_address = ", ".join(adr)
    try:
        phone = tree.xpath(".//a[contains(@href, 'tel:')]/text()")[0].strip()
    except IndexError:
        phone = SgRecord.MISSING

    return raw_address, phone


def fetch_data(sgw: SgWriter):
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for lat, lng in search:
        api = f"https://www.rightathome.net/location-finder?lat={lat}&lng={lng}"
        r = session.get(api)
        tree = html.fromstring(r.text)
        divs = tree.xpath("//div[@class='search-result']")

        for d in divs:
            location_name = "".join(d.xpath(".//h4/a/text()")).strip()
            page_url = "".join(d.xpath(".//h4/a/@href"))
            phone = "".join(
                d.xpath(".//a[contains(@href, 'tel:')]/strong/text()")
            ).strip()

            _tmp = []
            black = [
                "licence",
                "license",
                "number",
                "ahccs",
                "hcs",
                "hha",
                "ahca",
                "registration",
                "certification",
                "personal",
                "lic ",
                "provider",
                "#np",
                "rsa",
            ]
            lines = d.xpath(
                ".//div[@class='para']/p/a/text()|.//div[@class='para']/p/a/p/text()"
            )
            for line in lines:
                iscontinue = False
                t = line.replace("\xa0", " ").lower().strip()
                for b in black:
                    if b in t:
                        iscontinue = True
                if not t or iscontinue:
                    continue
                _tmp.append(line.replace("\xa0", " ").strip().replace("\n", " "))

            raw_address = ", ".join(_tmp).replace(",,", ",")
            incorrect = "".join(re.findall(regex, raw_address))
            if incorrect:
                correct = incorrect[:2] + " " + incorrect[2:]
                raw_address = re.sub(regex, correct, raw_address)

            if not raw_address:
                raw_address, phone = get_additional(page_url)

            street_address, city, state, postal = get_address(raw_address)

            try:
                text = "".join(d.xpath(".//script[@type='application/ld+json']/text()"))
                j = json.loads(text, strict=False)
                g = j.get("geo") or {}
                latitude = g.get("latitude")
                longitude = g.get("longitude")
            except:
                latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

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
                raw_address=raw_address,
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    regex = r"([A-Z]{2}\d{5})"
    locator_domain = "https://www.rightathome.net/"
    logger = sglog.SgLogSetup().get_logger(logger_name="rightathome.net")
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
