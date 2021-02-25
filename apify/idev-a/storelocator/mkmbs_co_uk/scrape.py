from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
import re
import copy

_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.5",
    "referer": "https://www.mkmbs.co.uk/",
    "origin": "https://www.mkmbs.co.uk",
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
}

_payload = {
    "latitude": "51.5073509",
    "longitude": "-0.1277583",
    "statuses": ["live"],
    "services": ["collection", "delivery"],
    "page_size": "150",
}

locations = []
maps = []


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


def map_path(data, schema):
    global maps
    for element, val in data.items():
        if isinstance(val, dict):
            map_path(val, schema)
        elif isinstance(val, list):
            for item in val:
                if item.get("_meta") and item["_meta"]["schema"] == schema:
                    maps.append(item)
                else:
                    map_path(item, schema)


def _fix(original):
    regex = re.compile(r'\\(?![/u"])')
    return regex.sub(r"\\\\", original)


def fetch_data():
    global maps
    global locations

    with SgRequests() as session:
        locator_domain = "https://www.mkmbs.co.uk/"
        base_url = "https://www.mkmbs.co.uk/mobify/proxy/base/services/branchservices.asmx/searchbranches"
        res = session.post(base_url, headers=_headers, json=_payload)
        links = json.loads(res.text)["branch_list"]
        for link in links:
            location_name = link["name"]
            url = "-".join(location_name.split(" ")[1:]).lower()
            page_url = urljoin(
                locator_domain,
                f"branch/{url}",
            )
            r1 = session.get(page_url)
            soup = bs(r1.text, "lxml")

            locations = []
            maps = []
            graphql = json.loads(
                _fix(
                    soup.find(
                        "script", string=re.compile("window.__PRELOADED_STATE__=")
                    ).string.replace("window.__PRELOADED_STATE__=", "")
                )
            )
            branch_schema = "https://www.mkmbs.co.uk/schema/branchinfo"
            branch_path(graphql["data"]["amplienceReducer"], branch_schema)
            map_schema = "https://www.mkmbs.co.uk/schema/map"
            map_path(graphql["data"]["amplienceReducer"], map_schema)

            _locations = copy.copy(locations)
            _maps = copy.copy(maps)
            for x in range(len(_locations)):
                location = _locations[x]
                coord = _maps[x]
                street_address = (
                    f"{location['addressLineOne']} {location.get('addressLineTwo', '')}"
                )
                city = location["townOrCity"]
                zip = location["postcode"]
                phone = location["phoneNumber"]
                hours_of_operation = (
                    location["openingHours"].replace("\\n\\n", "; ").replace("**", "")
                )
                yield SgRecord(
                    page_url=page_url,
                    store_number=link["id"],
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    zip_postal=zip,
                    country_code="uk",
                    latitude=coord.get("latitude"),
                    longitude=coord.get("longitude"),
                    phone=phone,
                    locator_domain=locator_domain,
                    hours_of_operation=hours_of_operation,
                )


if __name__ == "__main__":
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
