from typing import Iterable

from sglogging import sglog
from sgrequests import SgRequests
from sgscrape import simple_scraper_pipeline as sp
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data() -> Iterable[dict]:
    http = SgRequests()
    logzilla = sglog.SgLogSetup().get_logger(logger_name="CRAWLER")
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_results=100,
        expected_search_radius_miles=100,
    )

    url = "https://tools.usps.com/UspsToolsRestServices/rest/POLocator/findLocations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "Content-Type": "application/json",
    }

    for zipcode in search:
        data = (
            '{"maxDistance":"1000","lbro":"","requestType":"","requestServices":"","requestRefineTypes":"","requestRefineHours":"","requestZipCode":"'
            + str(zipcode)
            + '","requestZipPlusFour":""}'
        )
        try:
            results = http.post(url=url, data=data, headers=headers).json()["locations"]
            if len(results) > 0:
                for i in results:
                    try:
                        search.found_location_at(i["latitude"], i["longitude"])
                    except Exception:
                        logzilla.debug("Missing lat/lng")

                    try:
                        i["address3"] = i["address3"]
                    except Exception:
                        i["address3"] = ""

                    try:
                        i["address2"] = i["address2"]
                    except Exception:
                        i["address2"] = ""

                    try:
                        i["zip4"] = i["zip4"]
                    except Exception:
                        i["zip4"] = ""

                    yield i

        except Exception as e:
            logzilla.warning("Exc in fetch_data", exc_info=e)
            continue

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    x = x.replace("None", "")
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


def fix_minus(x):
    x = x.replace("None", "")
    h = []
    try:
        x = x.split("-")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = "-".join(h)
    except Exception:
        h = x

    return h


def parse_hours(k):
    h = []
    for i in k["dailyHoursList"]:
        try:
            h.append(
                i["dayOfTheWeek"]
                + ": "
                + i["times"][0]["open"]
                + "-"
                + i["times"][0]["close"]
            )
        except Exception:
            try:
                h.append(i["dayOfTheWeek"] + ": Closed")
            except Exception:
                continue
    return "; ".join(h)


def nice_hours(k):
    hours = "<MISSING>"
    prio = ["LOBBY", "POBACCESS", "APC"]
    dex = 0
    while hours == "<MISSING>" and dex < len(prio):
        for i in k:
            if prio[dex] == i["name"]:
                hours = parse_hours(i)
        dex += 1

    if hours == "<MISSING>":
        for i in k:
            hours = parse_hours(i)
            if hours != "<MISSING>":
                return hours

    return hours


def scrape():
    url = "https://www.usps.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["locationID"],
            value_transform=lambda x: "https://tools.usps.com/find-location.htm?location="
            + str(x),
        ),
        location_name=sp.MappingField(
            mapping=["locationName"],
            is_required=False,
        ),
        latitude=sp.MappingField(
            mapping=["latitude"],
            is_required=False,
        ),
        longitude=sp.MappingField(
            mapping=["longitude"], is_required=False, part_of_record_identity=True
        ),
        street_address=sp.MultiMappingField(
            mapping=[
                ["address1"],
                ["address2"],
                ["address3"],
            ],
            multi_mapping_concat_with=", ",
            is_required=False,
            part_of_record_identity=True,
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["city"],
            is_required=False,
        ),
        state=sp.MappingField(
            mapping=["state"],
            is_required=False,
        ),
        zipcode=sp.MultiMappingField(
            mapping=[["zip5"], ["zip4"]],
            multi_mapping_concat_with="-",
            value_transform=fix_minus,
            is_required=False,
        ),
        country_code=sp.MissingField(),
        phone=sp.MappingField(
            mapping=["phone"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["locationID"], part_of_record_identity=True
        ),
        hours_of_operation=sp.MappingField(
            mapping=["locationServiceHours"],
            part_of_record_identity=True,
            raw_value_transform=nice_hours,
        ),
        location_type=sp.MappingField(
            mapping=["locationType"], is_required=False, part_of_record_identity=True
        ),
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
