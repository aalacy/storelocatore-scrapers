from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def parse_store(x):
    k = {}
    k["error"] = False

    try:
        k["lat"] = x.split(",'", 1)[0]
    except:
        k["lat"] = "<MISSING>"

    try:
        k["lat"], k["lon"] = k["lat"].split(",", 1)
    except:
        k["lon"] = "<MISSING>"

    try:
        k["name"] = x.split("'<b>", 1)[1].split("&nbsp;", 1)[0]
    except:
        k["name"] = "<MISSING>"

    try:
        k["city"] = x.split("'<b>", 1)[1].split("&nbsp;", 2)[1]
    except:
        k["city"] = "<MISSING>"

    try:
        k["state"] = x.split("'<b>", 1)[1].split("&nbsp;", 2)[2].split("<", 1)[0]
    except:
        k["state"] = "<MISSING>"

    try:
        k["address"] = x.split("<br>", 2)[1]
    except:
        k["address"] = "<MISSING>"

    try:
        k["address"], k["zip"] = k["address"].split("&nbsp;", 1)
    except:
        k["zip"] = "<MISSING>"
        k["address"] = k["address"].replace("&nbsp;", "")
    try:
        k["phone"] = x.split("<br>", 3)[-2]
    except:
        k["phone"] = "<MISSING>"

    try:
        k["url"] = (
            "https://www.mycountymarket.com" + x.split('href="', 1)[1].split('">', 1)[0]
        )
    except:
        k["url"] = "<MISSING>"
        k["error"] = True

    return k


def para(tup):

    k = {}
    k["index"] = tup[0]
    k["requrl"] = tup[1]
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()

    son = session.get(k["requrl"], headers=headers)
    son = son.text

    try:
        k["hours"] = son.split("Store Hours", 1)
        k["hours"] = k["hours"][1].split("<div>", 1)
        k["hours"] = k["hours"][1].split("</")[0]
    except:
        k["hours"] = "<MISSING>"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.mycountymarket.com/shop/store-locator/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    scripts = soup.find_all("script", {"type": "text/javascript"})
    script = ""
    for i in scripts:
        if "createMapMarker" in i.text:
            script = i.text

    data = {}
    data["stores"] = []
    script = script.split("createMapMarker(")
    for i in script:
        data["stores"].append(parse_store(i))
        if data["stores"][-1]["error"] == True:
            data["stores"].pop()

    lize = utils.parallelize(
        search_space=[[counter, i["url"]] for counter, i in enumerate(data["stores"])],
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        data["stores"][i["index"]].update(i)
        yield data["stores"][i["index"]]
    data = "Finished grabbing data!!"
    logzilla.info(f"{data}")


def scrape():
    url = "https://www.mycountymarket.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["requrl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lon"]),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(
            mapping=["city"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=MappingField(
            mapping=["state"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=MappingField(
            mapping=["zip"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(
            mapping=["phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>").replace(
                "Phone: ", ""
            ),
            is_required=False,
        ),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="mycountymarket.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
