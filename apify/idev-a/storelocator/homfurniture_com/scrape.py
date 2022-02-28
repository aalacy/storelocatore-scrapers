from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import dirtyjson as json
import re
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
}

locator_domain = "https://www.homfurniture.com"
base_url = "https://www.homfurniture.com/info/our-stores/locations"


def _coord(websites, _city):
    for website in websites:
        for state in website["states"]:
            for city in state["cities"]:
                if city["city"] == _city:
                    return city


def fetch_data():
    with SgRequests() as http:
        d_url = (
            locator_domain
            + bs(http.get(base_url, headers=_headers), "lxml").find(
                "script", src=re.compile(r"meteor_js_resource")
            )["src"]
        )
        res = http.get(d_url, headers=_headers).text
        websites = json.loads(
            "{" + res.split("}});var n={")[1].split(".websites.find(function(")[0]
        )["websites"]
        states = json.loads(
            "["
            + res.replace("!0", "true")
            .replace("!1", "false")
            .split("}});var n=[")[1]
            .split('"superSaturdayRules.jsx"')[0]
            .strip()[:-2]
        )[2]["states"]
        for state in states:
            hours = []
            for city in state["cities"]:
                for hr in city.get("locationHours", []):
                    if hr["label"] == "store":
                        for hh in hr["days"]:
                            if hh["hours"] == "Opening Soon":
                                break
                            else:
                                hours.append(f"{hh['dayLabel']}: {hh['hours']}")

                for _ in city.get("locations", []):
                    page_url = locator_domain + _["url"]
                    phone = f"({_['phonePrefix']}) {_['phoneArea']}-{_['phoneLineNum']}"
                    coord = _coord(websites, _["city"])
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_["label"],
                        street_address=_["address"],
                        city=_["city"],
                        state=_["state"],
                        zip_postal=_["zip"],
                        country_code="US",
                        phone=phone,
                        latitude=coord["latitude"],
                        longitude=coord["longitude"],
                        locator_domain=locator_domain,
                        hours_of_operation="; ".join(hours),
                    )


if __name__ == "__main__":
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
