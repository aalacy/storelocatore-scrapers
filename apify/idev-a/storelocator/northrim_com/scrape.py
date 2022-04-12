from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from bs4 import BeautifulSoup as bs

logger = SgLogSetup().get_logger("northrim")

_headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "Content-type": "application/x-www-form-urlencoded",
    "Host": "northrim.locatorsearch.com",
    "Origin": "https://northrim.locatorsearch.com",
    "Referer": "https://northrim.locatorsearch.com/index.aspx?s=FCS",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}

locator_domain = "https://northrim.com/"
base_url = "https://northrim.locatorsearch.com/GetItems.aspx"
page_url = "https://northrim.com/About-Northrim/Contact-Us/Locations"


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


def fetch_records(search):
    # Need to add dedupe. Added it in pipeline.
    with SgRequests() as session:
        maxZ = search.items_remaining()
        total = 0
        for lat, lng in search:
            if search.items_remaining() > maxZ:
                maxZ = search.items_remaining()
            logger.info(("Pulling Geo Code %s..." % lat, lng))
            data = {
                "address": "32",
                "lat": str(lat),
                "lng": str(lng),
                "searchby": "FCS|ATMSF|",
                "rnd": "1621588075417",
            }
            locations = bs(
                session.post(base_url, headers=_headers, data=data)
                .text.replace("<![CDATA[", "")
                .replace("]]>", "")
                .replace("<br>", "<br/>")
                .replace("&gt;", ">"),
                "xml",
            ).select("marker")
            total += len(locations)
            for _ in locations:
                addr2 = list(_.select_one("add2").stripped_strings)
                hours = []
                for hh in _.select("div.infowindow table tr")[1:]:
                    temp = "".join(hh.stripped_strings)
                    if not temp or "Drive-up" in temp or "hour" in temp:
                        break
                    hours.append(temp)
                search.found_location_at(
                    _["lat"],
                    _["lng"],
                )
                c_s = addr2[0].split(",")
                s_z = c_s[1].strip().split()
                location_type = "<MISSING>"
                if "branch" in _["icon"]:
                    location_type = "branch"
                elif "atm" in _["icon"]:
                    location_type = "atm"
                yield SgRecord(
                    page_url=page_url,
                    location_name=_.select_one(".title").text.strip(),
                    street_address=_.select_one("add1").text,
                    city=c_s[0].strip(),
                    state=s_z[0].strip(),
                    zip_postal=s_z[1].strip() if len(s_z) > 1 else "",
                    country_code="US",
                    phone=addr2[-1] if _p(addr2[-1]) else "<MISSING>",
                    latitude=_["lat"],
                    longitude=_["lng"],
                    location_type=location_type,
                    locator_domain=locator_domain,
                    hours_of_operation="; ".join(hours),
                )

            progress = (
                str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
            )

            logger.info(
                f"found: {len(locations)} | total: {total} | progress: {progress}"
            )


if __name__ == "__main__":
    with SgRequests() as http:
        search = DynamicGeoSearch(
            country_codes=["us"], expected_search_radius_miles=100
        )
        with SgWriter(
            SgRecordDeduper(
                RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=10
            )
        ) as writer:
            for rec in fetch_records(search):
                writer.write_row(rec)
