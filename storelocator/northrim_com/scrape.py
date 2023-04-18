from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries


def _p(val):
    return (
        val.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .strip()
        .isdigit()
    )


locator_domain = "https://northrim.com/"
base_url = "https://northrim.locatorsearch.com/GetItems.aspx"
page_url = "https://northrim.com/About-Northrim/Contact-Us/Locations"


def fetch_data(sgw: SgWriter):

    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=100,
        max_search_results=None,
    )
    for lat, long in coords:
        coords.found_location_at(lat, long)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Origin": "https://northrim.locatorsearch.com",
            "Proxy-Authorization": "Basic ZG1pdHJpeTIyc2hhcGFAZ21haWwuY29tOnJxeFN6YzI0NnNzdnByVVZwdHJT",
            "Connection": "keep-alive",
            "Referer": "https://northrim.locatorsearch.com/index.aspx?s=FCS",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        data = {
            "lat": str(lat),
            "lng": str(long),
            "searchby": "FCS|ATMSF|",
            "rnd": "1655809100743",
        }
        locations = bs(
            session.post(base_url, headers=headers, data=data)
            .text.replace("<![CDATA[", "")
            .replace("]]>", "")
            .replace("<br>", "<br/>")
            .replace("&gt;", ">"),
            "xml",
        ).select("marker")

        for _ in locations:
            addr2 = list(_.select_one("add2").stripped_strings)
            hours = []
            for hh in _.select("div.infowindow table tr")[1:]:
                temp = "".join(hh.stripped_strings)
                if not temp or "Drive-up" in temp or "hour" in temp:
                    break
                hours.append(temp)

            c_s = addr2[0].split(",")
            s_z = c_s[1].strip().split()
            location_type = "<MISSING>"
            if "branch" in _["icon"]:
                location_type = "branch"
            elif "atm" in _["icon"]:
                location_type = "atm"

            row = SgRecord(
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

            sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)
