from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4


def para(k):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()

    url = k["page_url"] + "/about-us"
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")
    soup = soup.find("table", {"class": "uk-44-table"})
    h = []
    for i in soup.find_all("tr", {"class": "uk-44-row"}):
        j = [line for line in i.stripped_strings]
        if len(j) > 1:
            h.append(j[0] + ": " + j[-1])

    h.pop(-1)
    k["hours"] = "; ".join(h)
    return k


def fetch_data():
    # noqa para({"page_url":"https://www.porschebelfast.co.uk"})
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    # https://www.mitsubishi-motors.co.uk/dealer-locator
    url = "https://www.porsche.com/all/dealer2/GetLocationsWebService.asmx/GetLocationsInStateSpecialJS?market=uk&siteId=uk&language=none&state=&_locationType=Search.LocationTypes.Dealer&searchMode=proximity&searchKey=54.5789384%7C-5.9637819&address=BT12%206HR&maxproximity=44444&maxnumtries=44444&maxresults=44444&postalcode=BT12%206HR"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = b4(son.text, "lxml")

    results = []
    for i in soup.find_all("location"):
        k = {}
        k["id"] = i.find("id").text.strip() if i.find("id") else "<MISSING>"
        k["country"] = (
            i.find("market").text.strip() if i.find("market") else "<MISSING>"
        )
        k["latitude"] = (
            i.find("coordinates").find("lat").text.strip()
            if i.find("coordinates").find("lat")
            else "<MISSING>"
        )
        k["longitude"] = (
            i.find("coordinates").find("lng").text.strip()
            if i.find("coordinates").find("lng")
            else "<MISSING>"
        )
        k["name"] = i.find("name").text.strip() if i.find("name") else "<MISSING>"
        k["zipcode"] = (
            i.find("postcode").text.strip() if i.find("postcode") else "<MISSING>"
        )
        k["city"] = i.find("city").text.strip() if i.find("city") else "<MISSING>"
        k["address"] = (
            i.find("street").text.strip() if i.find("street") else "<MISSING>"
        )
        k["phone"] = i.find("phone").text.strip() if i.find("phone") else "<MISSING>"
        k["page_url"] = i.find("url1").text.strip() if i.find("url1") else "<MISSING>"
        k["hours"] = (
            i.find("openinghours").text.strip()
            if i.find("openinghours")
            else "<MISSING>"
        )
        k["type"] = (
            i.find("typecode").text.strip() if i.find("typecode") else "<MISSING>"
        )
        results.append(k)

    lize = utils.parallelize(
        search_space=results,
        fetch_results_for_rec=para,
        max_threads=20,
        print_stats_interval=20,
    )

    for i in lize:
        yield i

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
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


def scrape():
    url = "https://www.porsche.co.uk/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(mapping=["page_url"]),
        location_name=sp.MappingField(mapping=["name"], is_required=False),
        latitude=sp.MappingField(mapping=["latitude"]),
        longitude=sp.MappingField(mapping=["longitude"]),
        street_address=sp.MappingField(
            mapping=["address"], is_required=False, value_transform=fix_comma
        ),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MissingField(),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country"]),
        phone=sp.MappingField(mapping=["phone"]),
        store_number=sp.MappingField(mapping=["id"]),
        hours_of_operation=sp.MappingField(mapping=["hours"]),
        location_type=sp.MappingField(mapping=["type"]),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="Crawler",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
