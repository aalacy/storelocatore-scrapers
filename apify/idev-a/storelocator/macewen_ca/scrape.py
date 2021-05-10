from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import itertools as it
import datetime
from sgscrape.sgpostal import parse_address_intl
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("macewen")

_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/12.0 Mobile/15A372 Safari/604.1",
}


def fetch_data():
    locator_domain = "https://macewen.ca/"
    with SgRequests() as session:
        for i in it.chain(
            range(1106, 1117),
            range(1253, 1328),
            range(1354, 1365),
            range(1488, 1519),
            range(1569, 1672),
            range(2282, 2284),
            range(2351, 2353),
            range(2401, 2409),
            range(2889, 2891),
            range(2942, 2945),
        ):
            url = session.get("https://macewen.ca/?p=" + str(i)).url
            url_data = [
                "retail/find-a-macewen",
                "commercial/cardlock-network/cardlock-locations",
                "residential/locations",
            ]
            for i in url_data:
                if i in url:
                    res = session.get(url)
                    if res.status_code != 200:
                        continue
                    soup = bs(res.text, "lxml")
                    logger.info(url)
                    addr = parse_address_intl(
                        soup.select_one("div.address").text.strip()
                    )
                    latitude = (
                        soup.find("main", {"id": "main"})
                        .find("div", {"id": "vue"})
                        .find("single-place-map")[":lat"]
                    )
                    longitude = (
                        soup.find("main", {"id": "main"})
                        .find("div", {"id": "vue"})
                        .find("single-place-map")[":lng"]
                    )
                    phone = soup.find("a", href=re.compile(r"tel:")).text.strip()
                    hours = ""
                    if soup.find("div", class_="hours"):
                        dayofweek = datetime.datetime.today().strftime("%A")
                        hours = (
                            " ".join(
                                list(soup.find("div", class_="hours").stripped_strings)
                            )
                            .replace("Open Hours", "")
                            .replace("Today", dayofweek)
                        )
                    yield SgRecord(
                        page_url=url,
                        location_name=soup.select_one("div.title h2").text.strip(),
                        street_address=addr.street_address_1,
                        city=addr.city,
                        state=addr.state,
                        latitude=latitude,
                        longitude=longitude,
                        zip_postal=addr.postcode,
                        country_code="CA",
                        phone=phone,
                        locator_domain=locator_domain,
                        hours_of_operation=hours,
                    )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
