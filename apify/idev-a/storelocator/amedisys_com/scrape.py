from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup
import json

logger = SgLogSetup().get_logger("amedisys")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.amedisys.com/"
    base_url = "https://locations.amedisys.com/"
    numbers = []
    with SgRequests() as session:
        states = bs(session.get(base_url, headers=_headers).text, "lxml").select(
            "ul#bowse-content a"
        )
        logger.info(f"{len(states)} states found")
        for state in states:
            state_url = state["href"]
            logger.info(state_url)
            cities = bs(session.get(state_url, headers=_headers).text, "lxml").select(
                "ul.map-list a"
            )
            for city in cities:
                city_url = city["href"]
                locations = bs(
                    session.get(city_url, headers=_headers).text, "lxml"
                ).select("ul.map-list li.map-list-item-wrap")
                for _ in locations:
                    page_url = _.a["href"]
                    logger.info(
                        f"[{state.text.strip()}][{city.text.strip()}] {page_url}"
                    )
                    res = session.get(page_url, headers=_headers)
                    if res.url == page_url:
                        sp1 = bs(res.text, "lxml")
                        ss = json.loads(
                            sp1.find(
                                "script", type="application/ld+json"
                            ).string.strip()
                        )
                        for script in ss:
                            if _["data-lid"] in numbers:
                                continue
                            numbers.append(_["data-lid"])
                            hours = []
                            for hh in sp1.select("div.hours-wrapper div.day-hour-row"):
                                hours.append(
                                    f"{hh.select_one('span.daypart').text.strip()}: {''.join(hh.select_one('span.time').stripped_strings)}"
                                )
                            yield SgRecord(
                                page_url=page_url,
                                store_number=_["data-lid"],
                                location_type=_["data-particles"],
                                location_name=script["name"]
                                .replace("About", "")
                                .strip(),
                                street_address=script["address"]["streetAddress"],
                                city=script["address"]["addressLocality"],
                                state=script["address"]["addressRegion"],
                                zip_postal=script["address"]["postalCode"],
                                country_code="US",
                                phone=script["address"]["telephone"],
                                locator_domain=locator_domain,
                                latitude=script["geo"]["latitude"],
                                longitude=script["geo"]["longitude"],
                                hours_of_operation="; ".join(hours),
                            )
                    else:
                        data = json.loads(
                            res.text.split('"markerData":')[1]
                            .split('"locationSpecialties"')[0]
                            .strip()[:-1]
                        )
                        sp1 = bs(res.text, "lxml")
                        for script in data:
                            if script["lid"] in numbers:
                                continue
                            numbers.append(script["lid"])
                            info = json.loads(bs(script["info"], "lxml").text.strip())
                            street_address = info["address_1"]
                            if info["address_2"]:
                                street_address += " " + info["address_2"]
                            yield SgRecord(
                                page_url=page_url,
                                store_number=script["lid"],
                                location_name=f"{info['location_name']} in {info['city']}",
                                location_type=" ".join(
                                    info["location_name"].split(" ")[1:]
                                ),
                                street_address=street_address,
                                city=info["city"],
                                state=info["region"],
                                zip_postal=info["post_code"],
                                country_code="US",
                                locator_domain=locator_domain,
                                phone=sp1.select_one("a.phone").text.strip(),
                                latitude=script["lat"],
                                longitude=script["lng"],
                            )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
