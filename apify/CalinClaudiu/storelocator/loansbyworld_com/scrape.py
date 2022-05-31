from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgscrape.simple_scraper_pipeline import MultiMappingField
from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from bs4 import BeautifulSoup as b4
from sglogging import sglog

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def parse_hrs(soup):
    soup = b4(soup, "lxml")
    days = soup.find_all("span", {"class": "day"})
    hors = soup.find_all("span", {"class": "hours"})
    hours = ", ".join(
        [
            str(days[i].text.strip() + ": " + hors[i].text.strip())
            for i in range(len(days))
        ]
    )
    if "unday" not in hours.lower():
        spans = soup.find_all("span")
        for i in range(len(spans)):
            if "unday" in spans[i].text.lower():
                try:
                    hours = (
                        hours
                        + ", "
                        + spans[i].text.strip()
                        + ": "
                        + spans[i + 1].text.strip()
                    )
                except Exception as eh:
                    logzilla.error("eh", exc_info=eh)

    return hours


def fetch_data():
    def search_api(session, long):
        def actual_req(session, long):
            url = "https://www.loansbyworld.com/api/yext/geosearch"
            headers = {}

            headers["Content-Type"] = "application/json"
            data = str('{"location":"' + f"{long}" + '","radius":1000}')

            resp = session.post(url, headers=headers, data=data)
            try:
                resp = resp.json()
            except Exception as e:
                logzilla.error(f"{str(url)} \n {str(e)}", exc_info=e)
                return []
            return resp

        try:
            return actual_req(session, long)["data"]
        except Exception as smh:
            logzilla.error("smh", exc_info=smh)
            long = "0" + str(long)
            return actual_req(session, long)["data"]

    def fetch_sub(session, k):
        headers = {}
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"

        #%5Bstate%5D/%5Bcity%5D/%5BpostalCode%5D/%5BstoreId% # noqa
        # https://www.loansbyworld.com/locations/alabama/alabaster/35007/1521 # noqa
        url = (
            str(
                f"https://www.loansbyworld.com/locations/{k['state']['id']}/{k['address']['city']}/{k['address']['postalCode']}/{k['id']}"
            )
            .lower()
            .replace(" ", "-")
        )
        logzilla.info(url)
        resp = session.get(url, headers=headers)
        k["page_url"] = url
        k["hours"] = parse_hrs(resp.text)

        return k

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        expected_search_radius_miles=40,
        max_search_results=None,
    )

    with SgRequests() as session:
        for long in search:
            for result in search_api(session, long):
                try:
                    k = fetch_sub(session, result)
                    try:
                        k["address"]["line2"] = k["address"]["line2"]
                    except Exception:
                        k["address"]["line2"] = ""
                    yield k
                except Exception as e:
                    logzilla.error("", exc_info=e)
                    k = result
                    try:
                        k["address"]["line2"] = k["address"]["line2"]
                    except Exception:
                        k["address"]["line2"] = ""
                    k["hours"] = ""
                    yield k


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
    url = "https://www.loansbyworld.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["page_url"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        location_name=MappingField(
            mapping=["store"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        latitude=MappingField(
            mapping=["latitude"],
            part_of_record_identity=True,
        ),
        longitude=MappingField(mapping=["longitude"]),
        street_address=MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
            is_required=False,
        ),
        city=MappingField(
            mapping=["address", "city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=MappingField(
            mapping=["address", "region"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=MappingField(
            mapping=["address", "postalCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        country_code=MappingField(mapping=["address", "countryCode"]),
        phone=MappingField(
            mapping=["phone"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            is_required=False,
        ),
        store_number=MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="loansbyworld.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
        duplicate_streak_failure_factor=-1,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
