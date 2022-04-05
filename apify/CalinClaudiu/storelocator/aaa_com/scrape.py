from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgzip.dynamic import DynamicZipSearch, SearchableCountries


from sgrequests import SgRequests


def fix_record(record):
    try:
        record["operatingDays"] = record["operatingDays"]
    except Exception:
        record["operatingDays"] = {
            "operatingDay": {"days": "", "open": "", "close": ""}
        }
    try:
        record["operatingDays"]["operatingDay"] = record["operatingDays"][
            "operatingDay"
        ]
    except Exception:
        record["operatingDays"] = {
            "operatingDay": {"days": "", "open": "", "close": ""}
        }
    record["page_url"] = ""
    try:
        record["page_url"] = str(
            f"https://branches.northeast.aaa.com/{record['addresses']['address']['stateProv']['code']}/{record['addresses']['address']['cityName'].replace(' ','-')}"
        )
    except Exception:
        pass
    return record


def fetch_data():

    # possibly new API: https://branches.northeast.aaa.com/api/v1/stores/locations/ # noqa
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://tdr.aaa.com/tdrl/search.jsp?searchtype=O&radius=50000&format=json&ident=AAACOM&destination={zipCode}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        expected_search_radius_miles=90,
    )
    identities = set()
    maxZ = search.items_remaining()
    total = 0
    for zipcode in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0

        son = SgRequests.raise_on_err(
            session.get(url.format(zipCode=zipcode), headers=headers)
        ).json()
        try:
            results = son["aaa"]["services"]["travelItems"]["travelItem"]
        except Exception:
            continue
        if not isinstance(results, dict):
            for i in results:
                search.found_location_at(
                    i["position"]["latitude"], i["position"]["longitude"]
                )
                if (
                    str(i["id"] + i["itemName"] + i["position"]["latitude"])
                    not in identities
                ):
                    identities.add(
                        str(i["id"] + i["itemName"] + i["position"]["latitude"])
                    )
                    found += 1
                    record = fix_record(i)
                    yield record
        else:
            search.found_location_at(
                results["position"]["latitude"], results["position"]["longitude"]
            )
            if (
                str(
                    results["id"]
                    + results["itemName"]
                    + results["position"]["latitude"]
                )
                not in identities
            ):
                identities.add(
                    str(
                        results["id"]
                        + results["itemName"]
                        + results["position"]["latitude"]
                    )
                )
                found += 1
                record = fix_record(results)
                yield record

        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{zipcode} | found: {found} | total: {total} | progress: {progress}"
        )

    logzilla.info(f"Finished grabbing data!!")  # noqa


def nice_hours(operatingHours):
    if not isinstance(operatingHours, dict):
        res = []
        for i in operatingHours:
            res.append(i["days"] + ": " + i["open"] + "-" + i["close"])
        return "; ".join(res)
    else:
        if (
            len(
                str(
                    operatingHours["days"]
                    + ": "
                    + operatingHours["open"]
                    + "-"
                    + operatingHours["close"]
                    + ";"
                )
            )
            > 5
        ):
            res = str(
                operatingHours["days"]
                + ": "
                + operatingHours["open"]
                + "-"
                + operatingHours["close"]
                + ";"
            )
            res = list(res)
            if res[-1] == ";":
                res.pop(-1)
            return "".join(res)
        else:
            return "<MISSING>"


def scrape():
    url = "https://www.aaa.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url"],
        ),
        location_name=sp.MappingField(
            mapping=["itemName"],
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["position", "latitude"],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["position", "longitude"],
            part_of_record_identity=True,
        ),
        street_address=sp.MultiMappingField(
            mapping=["addresses", "address", "addressLine"],
            part_of_record_identity=True,
        ),
        city=sp.MappingField(
            mapping=["addresses", "address", "cityName"],
            part_of_record_identity=True,
        ),
        state=sp.MappingField(
            mapping=["addresses", "address", "stateProv", "code"],
            value_transform=lambda x: x.replace("99", "PR"),
        ),
        zipcode=sp.MappingField(
            mapping=["addresses", "address", "postalCode"],
            part_of_record_identity=True,
        ),
        country_code=sp.MappingField(
            mapping=["addresses", "address", "countryName", "code"],
        ),
        phone=sp.MappingField(
            mapping=["phones", "phone", "content"],
            is_required=False,
        ),
        store_number=sp.MappingField(
            mapping=["id"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["operatingDays", "operatingDay"],
            raw_value_transform=nice_hours,
        ),
        location_type=sp.MappingField(
            mapping=["type"],
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
