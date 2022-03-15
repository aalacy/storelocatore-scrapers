from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
import json
from sgpostal.sgpostal import parse_address_intl
from bs4 import BeautifulSoup as bs
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import re


locator_domain = "https://www.pizzahut.mu"
contact_us_url = "https://www.pizzahut.mu/contact-us/"
base_url = "https://www.google.com/maps/d/embed?mid=1ij51KPJm6MFRzgzBNbbI-agwyuma8p81"


def _headers():
    return {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
    }


def _d(locs, name, sa):
    latitude = longitude = ""
    for loc in locs:
        location_name = loc[5][0][1][0].replace("\\n", "").lower().strip()
        _nn = location_name.lower().split("hut")[1].strip().split()[0]
        if location_name == name.lower() or _nn in sa[0].lower():
            latitude = loc[1][0][0][0]
            longitude = loc[1][0][0][1]
            break

    return latitude, longitude


def fetch_data():
    with SgRequests() as session:
        sp1 = bs(session.get(contact_us_url, headers=_headers()).text, "lxml")
        locs = sp1.select("div.page-content div.vc_column_container.vc_col-sm-3")
        phone = (
            sp1.find("strong", string=re.compile(r"Phone Number", re.I))
            .text.split(":")[-1]
            .replace("Phone Number", "")
            .strip()
        )

        res = session.get(base_url, headers=_headers())
        cleaned = (
            res.text.replace("\\\\u003d", "=")
            .replace("\\\\u0026", "&")
            .replace("\\u0027", "'")
            .replace('\\\\"', "'")
            .replace('\\"', '"')
            .replace("\xa0", " ")
        )
        locations = json.loads(
            cleaned.split('var _pageData = "')[1].split('";</script>')[0]
        )
        for loc in locs:
            if loc.figure or not loc.h4:
                continue
            hours = []
            raw_address = list(loc.p.stripped_strings)
            addr = parse_address_intl(" ".join(raw_address) + ", Mauritius")
            for hh in list(loc.select("p")[1].stripped_strings)[1:]:
                if "Holidays" in hh:
                    continue
                hours.append(hh)

            location_name = loc.h4.text.strip()
            latitude, longitude = _d(
                locations[1][6][0][12][0][13][0], location_name, raw_address
            )
            yield SgRecord(
                page_url=contact_us_url,
                location_name=location_name,
                street_address=raw_address[0].replace(",", ""),
                city=addr.city,
                state=addr.state,
                zip_postal=addr.postcode,
                country_code="Mauritius",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                locator_domain=locator_domain,
                hours_of_operation="; ".join(hours),
                raw_address=" ".join(raw_address),
            )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
