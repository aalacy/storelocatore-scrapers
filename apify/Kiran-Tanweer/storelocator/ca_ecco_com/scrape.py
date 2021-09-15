from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://ca.ecco.com/en/store-locator"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    scripts = soup.find_all("script")
    theScript = None
    for i in scripts:
        if "storesJson" in i.text:
            theScript = i.text

    data = theScript.split("storesJson = ", 1)[1].split("}];", 1)[0] + "}]"

    theScript = theScript.split(".concat(")
    theScript.pop(0)
    for chunk in theScript:
        data = data + str("," + chunk.split(");", 1)[0])
    data = "[" + data + "]"
    data = json.loads(data)
    for chunk in data:
        for store in chunk:
            yield store

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("null", "").replace("None", "")
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def human_hours(x):
    hours = []
    for day in x:
        hours.append(" ".join(list(day.values())))
    return "; ".join(hours)


def scrape():
    url = "https://ca.ecco.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["address1"], ["address2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["city"],
        ),
        state=sp.MappingField(
            mapping=["stateCode"],
        ),
        zipcode=sp.MappingField(
            mapping=["postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["countryCode"],
        ),
        phone=sp.MappingField(
            mapping=["phone"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["storeID"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["storeHours"],
            raw_value_transform=human_hours,
        ),
        location_type=sp.MappingField(
            mapping=["isECCOStore"],
            value_transform=lambda x: x.replace("True", "ECCO").replace(
                "False", "<MISSING>"
            ),
        ),
        raw_address=sp.MappingField(
            mapping=["address"],
        ),
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
