import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


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

            _tmp = []
            black = [
                "licence",
                "license",
                "number",
                "ahccs",
                "airport",
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

            street_address = ", ".join(_tmp[:-1])
            csz = _tmp.pop()
            city = csz.split(",")[0].strip()
            csz = csz.split(",")[1].strip()
            state, postal = csz.split()
            phone = "".join(
                d.xpath(".//a[contains(@href, 'tel:')]/strong/text()")
            ).strip()

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
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.rightathome.net/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
