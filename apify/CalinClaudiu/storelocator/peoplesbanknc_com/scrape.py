from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://peoplesbanknc.com/ZagLocationsApi/Locations/Search"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Content-Type": "application/json",
    }
    data = '{"Radius":5000,"Latitude":35.7358579,"Longitude":-81.2188355,"Connectors":{"Website":{"icon":"locations.png","zIndex":10000,"selected":true}}}'
    session = SgRequests()
    son = session.post(url, headers=headers, data=data).json()
    son = json.loads(son)
    for i in son:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def nice_hours(x):
    soup = b4(x, "lxml")
    h = list(soup.stripped_strings)
    return str("; ".join(h)).replace("Hours;", "Hours:")


def scrape():
    url = "https://peoplesbanknc.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["NodeAliasPath"],
            value_transform=lambda x: str(url + x)
            .replace("//", "/")
            .replace("https:/", "https://"),
        ),
        location_name=sp.MappingField(
            mapping=["Name"],
        ),
        latitude=sp.MappingField(
            mapping=["Latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["Longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["Address1"], ["Address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["City"],
        ),
        state=sp.MappingField(
            mapping=["State"],
        ),
        zipcode=sp.MappingField(
            mapping=["Zip"],
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(mapping=["Phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["Id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["Lobby"], value_transform=nice_hours
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
