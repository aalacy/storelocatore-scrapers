from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from bs4 import BeautifulSoup as b4
from sglogging import sglog
import json

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def para(tup):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    k = {}
    page = None
    with SgRequests() as session:
        page = SgRequests.raise_on_err(session.get(tup[1], headers=headers)).text
    try:
        soup = b4(page, "lxml")

        script = soup.find_all(
            "script", {"type": "application/ld+json", "class": False}
        )
        script = script[0]
        k = json.loads(script.text)
    except Exception as e:
        logzilla.error(f"{str(e)}", exc_info=e)
        z = soup.find(
            "div", {"class": lambda x: x and all(i in x for i in ["col12", "stoney"])}
        )
        try:
            k["openingHours"] = (
                z.find("div", {"class": "loc_hours_holder"})
                .text.replace("Hours:", "")
                .replace("  ", "")
                .replace("\n", "; ")
            )
            k["name"] = z.find("div", {"class": "col9"}).find("h1").text.strip()
            k["@type"] = SgRecord.MISSING
        except Exception:
            pass

    k["index"] = tup[0]
    k["requrl"] = tup[1]
    yield k


def fetch_data():
    son = None
    with SgRequests() as session:
        url = "https://handandstone.ca/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&inLoad=false&max_results=20000&radius=100000"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        son = SgRequests.raise_on_err(session.get(url, headers=headers)).json()
    grabit = utils.parallelize(
        search_space=[[counter, i["url"]] for counter, i in enumerate(son)],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in grabit:
        for h in i:
            h["dic"] = son[h["index"]]
            if any(st in h["dic"]["phone"] for st in ["oming", "OPEN"]):
                h["dic"]["phone"] = "<MISSING>"
                h["@type"] = "Coming Soon"
            yield h


def fix_comma(x):
    h = []

    x = x.replace("None", "")
    try:
        x = x.split(",")
        for i in x:
            if len(i) > 1:
                h.append(i)
        h = ", ".join(h)
    except:
        h = x

    if len(h) < 2:
        h = "<MISSING>"

    return h


def scrape():
    url = "https://handandstone.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["dic", "url"],
            part_of_record_identity=True,
        ),
        location_name=MappingField(
            mapping=["name"], part_of_record_identity=True, is_required=False
        ),
        latitude=MappingField(
            mapping=["dic", "lat"],
            part_of_record_identity=True,
        ),
        longitude=MappingField(mapping=["dic", "lng"]),
        street_address=MultiMappingField(
            mapping=[["dic", "address"], ["dic", "address2"]],
            multi_mapping_concat_with=", ",
            part_of_record_identity=True,
            value_transform=fix_comma,
        ),
        city=MappingField(mapping=["dic", "city"]),
        state=MappingField(mapping=["dic", "state"]),
        zipcode=MappingField(mapping=["dic", "zip"]),
        country_code=MappingField(mapping=["dic", "country"]),
        phone=MappingField(
            mapping=["dic", "phone"],
            part_of_record_identity=True,
            is_required=False,
        ),
        store_number=MappingField(mapping=["dic", "id"]),
        hours_of_operation=MappingField(mapping=["openingHours"], is_required=False),
        location_type=MappingField(mapping=["@type"], is_required=False),
        raw_address=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="handandstone.ca",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
