from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("academybank")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://www.academybank.com"
    base_url = "https://www.academybank.com/locations"
    with SgRequests() as session:
        soup = bs(session.get(base_url, headers=_headers).text, "lxml")
        states = soup.select(".views-summary.views-summary-unformatted a")
        logger.info(f"{len(states)} found")
        for state in states:
            state_url = locator_domain + state["href"]
            logger.info(state_url)
            sp1 = bs(session.get(state_url, headers=_headers).text, "lxml")
            cities = sp1.select(".views-summary.views-summary-unformatted a")
            logger.info(f"{len(cities)} found")
            for city in cities:
                city_url = locator_domain + city["href"]
                logger.info(city_url)
                sp2 = bs(session.get(city_url, headers=_headers).text, "lxml")
                items = sp2.select("div.item-list ol li")
                logger.info(f"{len(items)} locations found")
                for _ in items:
                    page_url = (
                        locator_domain + _.select_one("div.field-content a")["href"]
                    )
                    coord = (
                        _.select_one("div.directions a")["href"]
                        .split("&daddr=")[1]
                        .split(",")
                    )
                    phone = ""
                    if _.select_one("div.phone"):
                        phone = _.select_one("div.phone").text.strip()
                    hours = []
                    for hh in list(_.select_one("div.hours").stripped_strings):
                        if "Video Banking Hours" in hh or "ATM" in hh:
                            break
                        hours.append(hh)
                    yield SgRecord(
                        page_url=page_url,
                        location_name=_.select_one("div.field-content a").text.strip(),
                        street_address=" ".join(
                            list(_.select_one("div.street-block").stripped_strings)
                        ),
                        city=_.select_one("span.locality").text.strip(),
                        state=_.select_one("span.state").text.strip(),
                        zip_postal=_.select_one("span.postal-code").text.strip(),
                        country_code="US",
                        phone=phone,
                        locator_domain=locator_domain,
                        latitude=coord[0],
                        longitude=coord[1],
                        location_type=list(_.select_one("div.type").stripped_strings)[
                            0
                        ].replace("What's This?", ""),
                        hours_of_operation="; ".join(hours).replace("–", "-"),
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
