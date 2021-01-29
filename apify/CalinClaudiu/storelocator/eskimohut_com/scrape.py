from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def para(url):
    session = SgRequests()
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    soup = b4(
        session.get("https://www.eskimohut.com" + url, headers=headers).text, "lxml"
    )

    k = {}
    k["status"] = True

    try:
        data = soup.find("div", {"data-lat": True})
    except Exception:
        data = "<MISSING>"

    try:
        addressData = list(soup.find("h3", {"id": "1603828934"}).stripped_strings)
        addressCopy = addressData
    except Exception:
        k["status"] = False
        addressData = "<MISSING>"

    k["page_url"] = "https://www.eskimohut.com" + url

    try:
        k["name"] = (
            soup.find("span", {"class": "m-font-size-36 lh-1 font-size-48"})
            .find("font")
            .text.strip()
        )
    except Exception:
        k["name"] = "<MISSING>"

    try:
        k["latitude"] = data["data-lat"]
        k["longitude"] = data["data-lng"]
    except Exception:
        k["latitude"] = "<MISSING>"
        k["longitude"] = "<MISSING>"

    try:
        k["hours"] = "; ".join(
            list(soup.find("h3", {"id": "1566722847"}).stripped_strings)
        )
    except Exception:
        k["hours"] = "<MISSING>"

    if len(addressData) >= 4:
        try:
            h = []
            for i in addressData[-1]:
                if i.isdigit():
                    h.append(i)
            k["phone"] = "".join(h)
            addressData.pop(-1)
        except Exception:
            k["phone"] = "<MISSING>"

        try:
            k["zip"] = addressData[-1]
            addressData.pop(-1)
        except Exception:
            k["zip"] = "<MISSING>"

        try:
            k["state"] = addressData[-1].split(",")[-1].strip()
        except Exception:
            k["state"] = "<MISSING>"

        try:
            k["city"] = addressData[-1].split(",")[0].strip()
            addressData.pop(-1)
        except Exception:
            k["city"] = "<MISSING>"

        try:
            h = []
            for i in addressData:
                h.append(i)
            k["address"] = ", ".join(h)
        except Exception:
            k["address"] = "<MISSING>"

    else:
        k["address"] = "<MISSING>"

    if k["address"] == "<MISSING>":
        addressData = addressCopy
        try:
            h = []
            for i in addressData[-1]:
                if i.isdigit():
                    h.append(i)
            k["phone"] = "".join(h)
            addressData.pop(-1)
        except Exception:
            k["phone"] = "<MISSING>"

        try:
            h = []
            copy = list(addressData[-1])
            i = copy[-1]
            copy.pop(-1)
            while i.isdigit() and len(copy) >= 1:
                h.append(i)
                i = copy[-1]
                copy.pop(-1)
            if i.isdigit():
                h.append(i)
            k["zip"] = []
            while len(h) > 0:
                k["zip"].append(h[-1])
                h.pop(-1)
            k["zip"] = "".join(k["zip"])
            addressData[-1] = addressData[-1].replace(k["zip"], "")
            if len(addressData[-1]) < 3:
                addressData.pop(-1)

        except Exception:
            k["zip"] = "<MISSING>"

        try:
            splitData = addressData[-1].split(",")
        except Exception:
            try:
                splitData = ",".join(addressData).split(",")
            except Exception:
                splitData = "<MISSING>"

        try:
            k["state"] = splitData[-1].strip()
            splitData.pop(-1)
        except Exception:
            k["state"] = "<MISSING>"

        try:
            if any(i.isdigit() for i in splitData[-1]):
                k["city"] = splitData[-1].strip()
                k["city"] = k["city"].split(" ")[-1].strip()
                if k["city"] == "Braunfels":
                    k["city"] = "New " + k["city"]

                    splitData[-1] = splitData[-1].replace(" New Braunfels", "")
            else:
                k["city"] = splitData[-1]
                splitData.pop(-1)
        except Exception:
            k["city"] = "<MISSING>"

        try:
            h = []
            for i in splitData:
                h.append(i)
            k["address"] = ", ".join(h)
        except Exception:
            k["address"] = "<MISSING>"

    return k


def fetch_data():
    para("/houston-westheimer")
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.eskimohut.com/find-a-hut"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    pages = soup.find_all("a", {"data-element-type": "dButtonLinkId"})
    h = []
    for i in pages:
        if "google" not in i["href"]:
            h.append(i["href"])
    pages = h
    lize = utils.parallelize(
        search_space=pages,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        if i["status"]:
            yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.eskimohut.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["page_url"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["latitude"],
        ),
        longitude=MappingField(
            mapping=["longitude"],
        ),
        street_address=MappingField(mapping=["address"], part_of_record_identity=True),
        city=MappingField(mapping=["city"], part_of_record_identity=True),
        state=MappingField(mapping=["state"], part_of_record_identity=True),
        zipcode=MappingField(mapping=["zip"], part_of_record_identity=True),
        country_code=MissingField(),
        phone=MappingField(mapping=["phone"], part_of_record_identity=True),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="Scraper",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
