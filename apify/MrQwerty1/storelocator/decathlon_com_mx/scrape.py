import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    params = [
        [
            "https://www.decathlon.com.mx/contactenos",
            "https://www.decathlon.com.mx/",
            "MX",
        ],
        [
            "https://www.decathlon.com.co/contactenos",
            "https://www.decathlon.com.co/",
            "CO",
        ],
        ["https://decathlon.lv/en/contact-us", "https://decathlon.lv/", "LV"],
        [
            "https://www.decathlon-rdc.com/nous-contacter",
            "https://www.decathlon-rdc.com/",
            "CD",
        ],
        [
            "https://www.decathlon.at/content/64-filialen-decathlon",
            "https://www.decathlon.at/",
            "AT",
        ],
        ["https://www.decathlon.ci/nous-contacter", "https://www.decathlon.ci/", "CI"],
        ["https://www.decathlon.cl/contactenos", "https://www.decathlon.cl/", "CL"],
        [
            "https://www.decathlon.co.ke/contact-us",
            "https://www.decathlon.co.ke/",
            "KE",
        ],
        [
            "https://www.decathlon.co.za/contact-us",
            "https://www.decathlon.co.za/",
            "ZA",
        ],
        [
            "https://www.decathlon.com.dz/nous-contacter",
            "https://www.decathlon.com.dz/",
            "DZ",
        ],
        [
            "https://www.decathlon.com.gh/contact-us",
            "https://www.decathlon.com.gh/",
            "GH",
        ],
        [
            "https://www.decathlon.com.gr/en/contact-us",
            "https://www.decathlon.com.gr/",
            "GR",
        ],
        [
            "https://www.decathlon.com.kh/en/content/6-our-stores-location",
            "https://www.decathlon.com.kh/",
            "KH",
        ],
        ["https://www.decathlon.eg/en/contact-us", "https://www.decathlon.eg/", "EG"],
        ["https://www.decathlon.ie/contact-us", "https://www.decathlon.ie/", "IE"],
        ["https://www.decathlon.tn/nous-contacter", "https://www.decathlon.tn/", "TN"],
    ]

    for param in params:
        api = param.pop(0)
        locator_domain = param.pop(0)
        country_code = param.pop(0)
        session = SgRequests(proxy_country=country_code.lower())
        r = session.get(api)
        tree = html.fromstring(r.text)
        text = "".join(
            tree.xpath("//script[contains(text(), 'store_marker.push(')]/text()")
        ).split("store_marker.push(")

        for t in text:
            if '"lat"' not in t:
                continue
            if "// " in t:
                t = t.split("// ")[0] + '"' + '"'.join(t.split("// ")[1].split('"')[1:])

            j = json.loads(t.split(");")[0].replace("&quot;", "'"))
            page_url = j.get("link") or api
            location_name = j.get("title")
            raw_address = j.get("address") or ""
            raw_address = (
                raw_address.replace("&#039", "'").replace(";", "").replace("&amp", "&")
            )
            street_address, city, state, postal = get_international(raw_address)
            if len(street_address) <= 7:
                street_address = raw_address.split(", ")[0]
            if not city:
                city = raw_address.split(",")[-2].strip()
            store_number = j.get("store_number")
            phone = j.get("phone")
            latitude = j.get("lat")
            longitude = j.get("lng")

            _tmp = []
            hours = j.get("hours") or "[]"
            hours = eval(hours)
            days = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
            for day, h in zip(days, hours):
                _tmp.append(f"{day}: {h[0]}")
            hours_of_operation = ";".join(_tmp)

            row = SgRecord(
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=postal,
                country_code=country_code,
                phone=phone,
                store_number=store_number,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
