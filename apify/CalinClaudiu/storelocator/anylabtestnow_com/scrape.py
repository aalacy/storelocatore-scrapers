from sgscrape import simple_scraper_pipeline as sp
from bs4 import BeautifulSoup as b4
from sgrequests.sgrequests import SgRequests
import json
import re


def fetch_data():
    url = "https://www.anylabtestnow.com/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    thescript = ""
    with SgRequests() as session:
        r = SgRequests.raise_on_err(session.get(url, headers=headers))
        soup = b4(r.text, "lxml")
        scripts = soup.find_all(
            "script", {"type": "rocketlazyloadscript", "data-rocket-type": True}
        )
        for script in scripts:
            if "var locations" in script.text:
                thescript = script.text

    k = thescript
    k = k.split("JSON.parse('")[1]
    k = k.split("]');")[0]
    k = k.split("[", 1)[1]
    k = '{"stores":[' + k + "]}"
    son = json.loads(k)
    for i in son["stores"]:
        yield i


def parsephn(bad):
    good = re.compile("[^0-9]")
    bad = good.sub("", bad)
    good = bad
    return good


def scrape():
    url = "https://www.anylabtestnow.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["url"]),
        location_name=sp.MappingField(mapping=["title"]),
        latitude=sp.MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=sp.MappingField(mapping=["longitude"], part_of_record_identity=True),
        street_address=sp.MappingField(
            mapping=["address"],
            value_transform=lambda x: re.sub("^\\D+(\\d)", "\\1", x),
        ),
        city=sp.MappingField(mapping=["city"]),
        state=sp.MappingField(mapping=["state"]),
        zipcode=sp.MappingField(mapping=["zip"]),
        country_code=sp.ConstantField("US"),
        phone=sp.MappingField(
            mapping=["phone"], value_transform=parsephn, part_of_record_identity=True
        ),
        store_number=sp.MappingField(mapping=["id"], part_of_record_identity=True),
        hours_of_operation=sp.MappingField(
            mapping=["hours"],
            value_transform=lambda x: x.replace("{'day': '", "")
            .replace("', 'start': '", " ")
            .replace("', 'end': '", "-")
            .replace("'}", "")
            .replace("[", "")
            .replace("]", ""),
            part_of_record_identity=True,
        ),
        location_type=sp.MappingField(
            mapping=["services"],
            value_transform=lambda x: x.replace("[", "")
            .replace("]", "")
            .replace("'", ""),
            is_required=False,
        ),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="anylabtestnow.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
