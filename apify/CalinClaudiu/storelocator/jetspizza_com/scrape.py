from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def para(url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")

    data = soup.find(
        "div", {"class": lambda x: x and "store__body" in x and "pge__content" in x}
    )

    k = {}

    k["CustomUrl"] = url

    try:
        k["Latitude"] = (
            data.find("button", {"class": "store__map-container"})["style"]
            .split(")/")[1]
            .split(",")[1]
        )
    except:
        k["Latitude"] = "<MISSING>"

    try:
        k["Longitude"] = (
            data.find("button", {"class": "store__map-container"})["style"]
            .split(")/")[1]
            .split(",")[0]
        )
    except:
        k["Longitude"] = "<MISSING>"

    k["Name"] = "<MISSING>"

    try:
        if "Greater Columbus" in data.find("p", {"class": "store__box-p"}).text.strip():
            k["Address"] = ", ".join(
                data.find("p", {"class": "store__box-p"}).text.split(",")[1:]
            ).strip()
        else:
            k["Address"] = data.find("p", {"class": "store__box-p"}).text.strip()
    except:
        k["Address"] = "<MISSING>"

    try:
        k["City"] = k["Address"].split(",")[-2]
    except:
        k["City"] = "<MISSING>"

    try:
        k["State"] = k["Address"].split(",")[-1].strip()
        k["State"] = k["State"].split(" ")[0]
    except:
        k["State"] = "<MISSING>"

    try:
        k["Zip"] = k["Address"].split(",")[-1].strip()
        k["Zip"] = k["Zip"].split(" ")[1]
    except:
        k["Zip"] = "<MISSING>"

    try:
        k["Phone"] = (
            data.find("div", {"class": lambda x: x and "store__box--phone" in x})
            .find("p", {"class": "store__box-p"})
            .text.strip()
        )
    except:
        k["Phone"] = "<MISSING>"

    try:
        h = list(data.find("div", {"class": "store__box-hours-group"}).stripped_strings)
        k["OpenHours"] = "; ".join(h)
    except:
        k["OpenHours"] = "<MISSING>"

    try:
        k["Address"] = ", ".join(k["Address"].split(",")[:-2])
    except:
        k["Address"] = "<MISSING>"

    k["StoreNumber"] = soup.body["class"][-1].split("-")[-1]

    if "coming soon" in soup.find(class_="store__box-heading").text.lower():
        k["IsActive"] = "Coming Soon"
    else:
        k["IsActive"] = "Open"

    k["Country"] = "US"

    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.jetspizza.com/stores/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    states = []
    stores = []

    logzilla.info("Grabbing state links")
    for i in soup.find("div", {"class": "pge-find-store__states"}).find_all(
        "a", {"class": "pge-find-store__state-item"}
    ):
        states.append(i["href"])

    url = "https://locations.tacojohns.com/"
    logzilla.info("Grabbing store links")

    for i in states:
        son = session.get(i, headers=headers)
        soup = b4(son.text, "lxml")
        links = soup.find("div", {"class": "pge-find-store__entries"})
        for j in links.find_all("a", {"class": "locator-results__store-detail"}):
            if "/stores" in j["href"] and "//il" not in j["href"]:
                stores.append(j["href"])

    logzilla.info("Grabbing store data")

    lize = utils.parallelize(
        search_space=stores,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )

    for i in lize:
        yield i

    logzilla.info("Finished grabbing data!!")


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
    if "Columbus," in h:
        h = h.split(",")[0].strip()
    return h.replace("  ", " ")


def scrape():
    url = "https://www.jetspizza.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["CustomUrl"]),
        location_name=sp.MappingField(
            mapping=["Name"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=sp.MappingField(mapping=["Latitude"]),
        longitude=sp.MappingField(mapping=["Longitude"]),
        street_address=sp.MappingField(mapping=["Address"], value_transform=fix_comma),
        city=sp.MappingField(
            mapping=["City"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        state=sp.MappingField(
            mapping=["State"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        zipcode=sp.MappingField(
            mapping=["Zip"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        country_code=sp.MappingField(mapping=["Country"]),
        phone=sp.MappingField(
            mapping=["Phone"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        store_number=sp.MappingField(
            mapping=["StoreNumber"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(mapping=["OpenHours"]),
        location_type=sp.MappingField(mapping=["IsActive"]),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="jetspizza.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
