from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def get_storeCA(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    r = session.get(url, headers=headers)
    k = {}
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("main", {"id": "store-container", "class": True, "data-id": True})
    k["url"] = url
    try:
        k["name"] = data.find("h2", {"class": "store__subtitle"}).text
    except:
        k["name"] = "<MISSING>"

    if k["name"] == "":
        try:
            k["name"] = data.find("h1", {"class": "store__title"}).text
        except:
            k["name"] = "<MISSING>"

    try:
        k["lat"] = data["data-store-lat"]
    except:
        k["lat"] = "<MISSING>"

    try:
        k["lng"] = data["data-store-lng"]
    except:
        k["lng"] = "<MISSING>"

    try:
        k["address"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        if k["address"].count(",") == "3":
            k["address"] = " ".join(k["address"].split(",")[:1].split(" ")[:-2])
        else:
            k["address"] = " ".join(k["address"].split(",")[0].split(" ")[:-2])
    except:
        k["address"] = "<MISSING>"

    try:
        k["city"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["city"] = k["city"].split(",")[-2]
    except:
        k["city"] = "<MISSING>"

    try:
        k["state"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["state"] = k["state"].split(",")[-1]
    except:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["zip"] = " ".join(k["zip"].split(",")[-3].split(" ")[-2:])
    except:
        k["zip"] = "<MISSING>"

    try:
        k["country"] = "CA"
    except:
        k["country"] = "<MISSING>"

    try:
        k["phone"] = (
            data.find("a", {"class": "phone"}).find("span", {"class": "text"}).text
        )
    except:
        k["phone"] = "<MISSING>"

    try:
        k["id"] = data["data-id"]
    except:
        k["id"] = "<MISSING>"

    try:
        j = []
        k["hours"] = data.find("div", {"class": "store__hours"}).find(
            "ul", {"data-expandable-area": True, "data-expandable": True}
        )
        k["hours"] = k["hours"].find_all("li")
        for i in k["hours"]:
            j.append(i.text)
        k["hours"] = "; ".join(j)
        k["hours"] = k["hours"].replace("\n", " ")

    except:
        k["hours"] = "<MISSING>"

    try:
        k["type"] = " ".join(data["class"])
        k["type"] = k["type"].split("type-")[1].split(" ", 1)[0]
    except:
        k["type"] = "<MISSING>"
    return k


def get_storeUS(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    r = session.get(url, headers=headers)
    k = {}
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("main", {"id": "store-container", "class": True, "data-id": True})
    k["url"] = url
    try:
        k["name"] = data.find("h1", {"class": "store__title"}).text
    except:
        k["name"] = "<MISSING>"

    if k["name"] == "":
        try:
            k["name"] = data.find("h2", {"class": "store__subtitle"}).text
        except:
            k["name"] = "<MISSING>"

    try:
        k["lat"] = data["data-store-lat"]
    except:
        k["lat"] = "<MISSING>"

    try:
        k["lng"] = data["data-store-lng"]
    except:
        k["lng"] = "<MISSING>"

    try:
        k["address"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        if k["address"].count(",") == "3":
            k["address"] = " ".join(k["address"].split(",")[:1].split(" ")[:-1])
        else:
            k["address"] = " ".join(k["address"].split(",")[0].split(" ")[:-1])
    except:
        k["address"] = "<MISSING>"

    try:
        k["city"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["city"] = k["city"].split(",")[-2]
    except:
        k["city"] = "<MISSING>"

    try:
        k["state"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["state"] = k["state"].split(",")[-1]
    except:
        k["state"] = "<MISSING>"

    try:
        k["zip"] = (
            data.find("li", {"class": "store__loc-address"})
            .find("span", {"class": "text"})
            .text
        )
        k["zip"] = k["zip"].split(",")[-3].split(" ")[-1]
    except:
        k["zip"] = "<MISSING>"

    try:
        k["country"] = "US"
    except:
        k["country"] = "<MISSING>"

    try:
        k["phone"] = (
            data.find("a", {"class": "phone"}).find("span", {"class": "text"}).text
        )
    except:
        k["phone"] = "<MISSING>"

    try:
        k["id"] = data["data-id"]
    except:
        k["id"] = "<MISSING>"

    try:
        j = []
        k["hours"] = data.find("div", {"class": "store__hours"}).find(
            "ul", {"data-expandable-area": True, "data-expandable": True}
        )
        k["hours"] = k["hours"].find_all("li")
        for i in k["hours"]:
            j.append(i.text)
        k["hours"] = "; ".join(j)
        k["hours"] = k["hours"].replace("\n", " ")

    except:
        k["hours"] = "<MISSING>"

    try:
        k["type"] = " ".join(data["class"])
        k["type"] = k["type"].split("type-")[1].split(" ", 1)[0]
    except:
        k["type"] = "<MISSING>"
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="checkmate")
    url = "https://www.armaniexchange.com/experience/us/store-locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }
    session = SgRequests()
    logzilla.info(f"Generating request links")  # noqa
    son = session.get(url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    gen = soup.find_all("li", {"class": "store-locator__stores-list-item"})
    links = []
    for i in gen:
        tex = (
            i.find("button", {"class": "store-locator__stores-button"})
            .find("span", {"class": "text"})
            .text
        )
        if "Canada" in tex or "United States" in tex:
            links.append(
                [
                    j["href"]
                    for j in i.find(
                        "div", {"class": "store-locator__stores-details"}
                    ).find_all("a", {"class": "store-locator__stores-details-name"})
                ]
            )
    logzilla.info(f"Grabbing {len(links[0])} locations from Canada")
    for i in links[0]:
        k = get_storeCA(i)
        yield k
    logzilla.info(f"Grabbing {len(links[1])} locations from USA")
    for i in links[1]:
        k = get_storeUS(i)
        yield k

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://armaniexchange.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["zip"]),
        country_code=MappingField(mapping=["country"]),
        phone=MappingField(mapping=["phone"]),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(mapping=["hours"]),
        location_type=MappingField(mapping=["type"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="armaniexchange.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
