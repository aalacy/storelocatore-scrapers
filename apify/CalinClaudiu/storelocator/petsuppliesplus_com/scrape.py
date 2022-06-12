from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sglogging import sglog


def get_soup(url):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    soup = session.get(url, headers=headers).text
    soup = b4(soup, "lxml")
    return soup


def para(tup):

    soup = get_soup(tup[1])
    counter = 0
    while "Looks like server failed to load your request" in soup.text and counter < 15:
        soup = get_soup(tup[1])
        counter += 1
    k = {}
    k["index"] = tup[0]
    k["requrl"] = tup[1]
    try:
        k["openingHoursSpecification"] = (
            "; ".join(list(soup.find("div", {"class": "hours"}).stripped_strings))
            .replace("Hours; ", "")
            .strip()
        )
    except Exception:
        k["openingHoursSpecification"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="sgzip")
    url = "https://www.petsuppliesplus.com"
    testur = "https://www.petsuppliesplus.com/api/sitecore/StoreLocator/Search?Latitude=40.7127753&Longitude=-74.0059728&Radius=6000&FilterType=1&NumberOfRecords=6000&NumberOfRecordsToSkip=0"
    headerz = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    headerz["Content-Type"] = "application/json"
    headerz["Content-Length"] = "0"
    session = SgRequests()
    son = session.post(url=testur, headers=headerz).json()
    if len(son["NearbyStores"]) > 0:
        j = utils.parallelize(
            search_space=[
                [counter, url + i["StorePageUrl"]]
                for counter, i in enumerate(son["NearbyStores"])
            ],
            fetch_results_for_rec=para,
            max_threads=10,
            print_stats_interval=10,
        )
        for p in j:
            kk = p["index"]
            son["NearbyStores"][kk]["data"] = p
            son["NearbyStores"][kk]["hourz"] = son["NearbyStores"][kk]["data"][
                "openingHoursSpecification"
            ]
            yield son["NearbyStores"][kk]
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
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


def determine_type(x):
    result = "<MISSING>"
    r1 = None
    r2 = None
    if x[0]:
        r1 = "Coming Soon"
    if x[1]:
        r2 = "Permanently Closed"

    if r1:
        result = r1
        if r2:
            result = r1 + ", " + r2
    if r2:
        result = r2
        if r1:
            result = r1 + ", " + r2

    return result


def scrape():
    url = "https://petsuppliesplus.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["data", "requrl"]),
        location_name=MappingField(mapping=["Name"]),
        latitude=MappingField(mapping=["LatPos"]),
        longitude=MappingField(mapping=["LngPos"]),
        street_address=MultiMappingField(
            mapping=[["Address1"], ["Address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=MappingField(mapping=["City"]),
        state=MappingField(mapping=["StateCode"]),
        zipcode=MappingField(mapping=["Zip"]),
        country_code=MissingField(),
        phone=MappingField(mapping=["Phone"], is_required=False),
        store_number=MappingField(mapping=["StoreId"], part_of_record_identity=True),
        hours_of_operation=MappingField(mapping=["hourz"]),
        location_type=MultiMappingField(
            mapping=[["IsComingSoon"], ["IsClosedPermanently"]],
            raw_value_transform=determine_type,
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="petsuppliesplus.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
