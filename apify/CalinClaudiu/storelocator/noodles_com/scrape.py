from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import bs4
from typing import Callable
from typing import List
from typing import Dict
from bs4 import BeautifulSoup
import json


def fetch_axml(
    request_url: str,
    root_node_name: str,
    location_node_name: str,
    method: str = "GET",
    location_parser: Callable[[bs4.Tag], dict] = utils.xml_to_dict,
    location_node_properties: Dict[str, str] = {},
    query_params: dict = {},
    data_params: dict = {},
    headers: dict = {},
    xml_parser: str = "lxml",
    retries: int = 10,
) -> List[dict]:

    response = net_utils.fetch_data(
        request_url=request_url,
        method=method,
        data_params=data_params,
        query_params=query_params,
        headers=headers,
        retries=retries,
    )

    xml_result = BeautifulSoup(response.text, "lxml")

    root_node = xml_result.find(root_node_name)

    location_nodes = root_node.find_all(location_node_name, location_node_properties)

    results = []
    for location in location_nodes:
        results.append({"dic": location_parser(location), "requrl": request_url})
    return results


def fetch_data():
    url = "https://locations.noodles.com/index.html"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    states = net_utils.fetch_xml(
        root_node_name="body",
        location_node_name="li",
        location_node_properties={"class": "c-directory-list-content-item"},
        request_url=url,
        headers=headers,
    )
    stores = {"state": [], "city": [], "store": []}
    url = "https://locations.noodles.com/"
    for j in states:
        link = list(j)[0].split("href=")[1]
        count = link.count("/")
        if count == 0:
            stores["state"].append(url + link)
        elif count == 1:
            stores["city"].append(url + link)
        else:
            stores["store"].append(url + link)
    # odd sitemap may show states, cities, or individual stores,
    # building states list

    for i in stores["state"]:
        cities = net_utils.fetch_xml(
            root_node_name="body",
            location_node_name="li",
            location_node_properties={"class": "c-directory-list-content-item"},
            request_url=i,
            headers=headers,
        )
        for j in cities:
            link = list(j)[0].split("href=")[1]
            count = link.count("/")
            if count == 1:
                stores["city"].append(url + link)
            else:
                stores["store"].append(url + link)
    # building city list

    for i in stores["city"]:
        store = net_utils.fetch_xml(
            root_node_name="body",
            location_node_name="h2",
            location_node_properties={"class": "c-location-grid-item-title"},
            request_url=i,
            headers=headers,
        )
        for j in store:
            link = i[0:-5] + "/" + list(j)[0].split("/")[-1].split(" title")[0]
            stores["store"].append(link)
    # building final store list

    j = utils.parallelize(
        search_space=stores["store"],
        fetch_results_for_rec=lambda x: fetch_axml(
            root_node_name="body",
            location_node_name="div",
            location_node_properties={"class": "nap-container row"},
            request_url=x,
            headers=headers,
        ),
        max_threads=15,
        print_stats_interval=15,
    )
    for i in j:
        for h in i:
            yield h


def pretty_hours(k):
    try:
        k = k.split("data-days=")[1]
        k = k.split(" data-showopentoday")[0]
        k = '{"hours":' + k + "}"
        k = json.loads(k)
        x = []
        for i in k["hours"]:
            d = ""
            d = i["day"] + " : "
            if len(i["intervals"]) != 0:
                d = (
                    d
                    + str(i["intervals"][0]["start"])
                    + "-"
                    + str(i["intervals"][0]["end"])
                )
            else:
                d = d + "Closed"
            x.append(d)
        x = ", ".join(x)
        return x
    except Exception:
        return "<MISSING>"


def scrape():
    url = "https://noodles.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["requrl"]),
        location_name=MappingField(
            mapping=[
                "dic",
                "div class=[nap-col, nap-col--large]",
                "div class=[white-container]",
                "div class=[c-location-title-wrapper]",
                "h1 class=[c-location-title] aria-level=1 id=location-name itemprop=name",
                "span class=[location-name-geo]",
                "span class=[location-name-geo]",
            ]
        ),
        latitude=MappingField(
            mapping=[
                "dic",
                "div class=[nap-col]",
                "div class=[nap-address-wrapper]",
                "span class=[coordinates] itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates",
            ],
            value_transform=lambda x: x.split("itemprop=latitude content=")[1].split(
                "'"
            )[0],
        ),
        longitude=MappingField(
            mapping=[
                "dic",
                "div class=[nap-col]",
                "div class=[nap-address-wrapper]",
                "span class=[coordinates] itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates",
            ],
            value_transform=lambda x: x.split("itemprop=longitude content=")[1].split(
                "'"
            )[0],
        ),
        street_address=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("c-address-street-1]': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", ""),
        ),
        city=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("itemprop=addressLocality': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", ""),
        ),
        state=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("addressRegion': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", ""),
        ),
        zipcode=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("emprop=postalCode': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", ""),
        ),
        country_code=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("itemprop=addressCountry': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", ""),
        ),
        phone=MappingField(
            mapping=["dic", "div class=[nap-col]", "div class=[nap-address-wrapper]"],
            value_transform=lambda x: x.split("itemprop=telephone id=telephone': ")[-1]
            .split("}")[0]
            .replace('"', "")
            .replace("'", "")
            .replace(
                "{div class=[nap-address-header]: {i class=[fa, fa-map-marker] aria-hidden=true: {",
                "<MISSING>",
            )
            .strip(),
        ),
        store_number=MissingField(),
        hours_of_operation=MappingField(
            mapping=["dic", "div class=[nap-col]-2"], value_transform=pretty_hours
        ),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="noodles.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
