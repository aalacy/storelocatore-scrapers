from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json


def para(k):
    payload = {
        "query": "query StoreById($id: String!) {\n  storeById(input: {id: $id}) {\n    ...storeAttributes\n    clickAndCollect\n    facilities {\n      facility\n      facilityIcon\n    }\n  }\n}\n\nfragment storeAttributes on Store {\n  sapSiteId\n  name\n  uri\n  streetAddress\n  localArea\n  city\n  county\n  postcode\n  country\n  phone\n  location {\n    lat\n    lon\n  }\n  tillTimes\n  openingHours {\n    day\n    open\n    close\n  }\n  seoText {\n    type\n    text\n    spans {\n      start\n      end\n      type\n    }\n  }\n}\n",
        "variables": {"id": k["uri"]},
    }
    headers = {}
    headers["Content-Type"] = "application/json"
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    url = "https://was.dunelm.com/graphql"
    session = SgRequests()
    son = session.post(url, headers=headers, json=payload).json()

    return son["data"]["storeById"][0]


def fetch_data():
    para(
        {"uri": "wakefield", "location": {"lat": 53.67614, "lon": -1.5026739999999994}}
    )
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")

    url = "https://www.dunelm.com/stores"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    scripts = soup.find_all("script", {"type": "application/javascript"})
    thescript = ""

    for i in scripts:
        if "REDUX_STATE" in i.text:
            thescript = i.text

    thescript = thescript.split("REDUX_STATE", 1)[-1]
    thescript = "{" + thescript.split("={", 1)[1]
    thescript = thescript.split("window.DUNELM_FEATURE_FL", 1)[0]
    thescript = thescript.rsplit(";", 1)[0]
    thescript = thescript.replace("undefined", '"undefined"')
    thescript = json.loads(thescript)
    data = thescript

    lize = utils.parallelize(
        search_space=data["stores"]["data"],
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )

    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def nice_hours(k):
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    h = []
    hours = "<MISSING>"
    for i in k:
        h.append(str(days[i["day"]] + ": " + i["open"] + "-" + i["close"]))
    if len(h) > 0:
        hours = "; ".join(h)
    return hours


def scrape():
    url = "https://www.dunelm.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["uri"],
            value_transform=lambda x: "https://www.dunelm.com/stores/" + x,
        ),
        location_name=sp.MappingField(mapping=["name"], is_required=False),
        latitude=sp.MappingField(mapping=["location", "lat"]),
        longitude=sp.MappingField(mapping=["location", "lon"]),
        street_address=sp.MultiMappingField(
            mapping=[["streetAddress"], ["localArea"]],
            is_required=False,
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["county"], is_required=False),
        zipcode=sp.MappingField(mapping=["postcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(
            mapping=["sapSiteId"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(
            mapping=["openingHours"], raw_value_transform=nice_hours
        ),
        location_type=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
