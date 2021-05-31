from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
import re
import copy
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("mkmbs")

_headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

locations = []


def branch_path(data, schema):
    global locations
    for element, val in data.items():
        if isinstance(val, dict):
            branch_path(val, schema)
        elif isinstance(val, list):
            for item in val:
                if item.get("_meta") and item["_meta"]["schema"] == schema:
                    locations.append(item)
                else:
                    branch_path(item, schema)


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original)


def fetch_data():
    global locations

    streets = []
    with SgRequests() as session:
        locator_domain = "https://www.mkmbs.co.uk/"
        base_url = "https://www.mkmbs.co.uk/mobify/proxy/base/"
        links = json.loads(
            bs(session.get(base_url, headers=_headers).text, "lxml")
            .select_one("div#mobify_branchdata")
            .text.replace("&quot;", '"')
        )["branch_list"]
        logger.info(f"{len(links)} found")
        for link in links:
            location_name = link["name"]
            logger.info(location_name)
            url = "-".join(location_name.split(" ")[1:]).lower()
            page_url = urljoin(
                locator_domain,
                f"branch/{url}",
            )
            soup = bs(session.get(page_url).text, "lxml")

            locations = []
            graphql = json.loads(
                _fix(
                    soup.find(
                        "script", string=re.compile("window.__PRELOADED_STATE__=")
                    ).string.replace("window.__PRELOADED_STATE__=", "")
                )
            )
            branch_schema = "https://www.mkmbs.co.uk/schema/branchinfo"
            branch_path(graphql["data"]["amplienceReducer"], branch_schema)

            _locations = copy.copy(locations)
            for x in range(len(_locations)):
                location = _locations[x]
                street_address = (
                    f"{location['addressLineOne']} {location.get('addressLineTwo', '')}"
                )
                if street_address in streets:
                    logger.info(f"duplicated [{page_url}]")
                    continue
                streets.append(street_address)
                hours_of_operation = (
                    location["openingHours"].replace("\\n\\n", "; ").replace("**", "")
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=link["id"],
                    location_name=location_name,
                    street_address=street_address,
                    city=location["townOrCity"],
                    state=location.get("county", ""),
                    zip_postal=location["postcode"],
                    country_code="uk",
                    latitude=link["latitude"],
                    longitude=link["longitude"],
                    phone=location["phoneNumber"],
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
