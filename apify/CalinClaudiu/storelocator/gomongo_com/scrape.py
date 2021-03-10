from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgzip.dynamic import DynamicZipSearch, SearchableCountries

from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=2500&location="
    ext = "&limit=50&api_key=24d4371c65ff61f3c305049db7b9f5de&v=20181201"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()

    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=2500,
        max_search_results=50,
    )
    identities = set()
    maxZ = search.items_remaining()
    total = 0
    for zipcode in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0

        son = session.get(url + '"' + str(zipcode) + '"' + ext, headers=headers).json()

        for i in son["response"]["entities"]:
            search.found_location_at(
                i["yextDisplayCoordinate"]["latitude"],
                i["yextDisplayCoordinate"]["longitude"],
            )
            if i["featuredMessage"]["url"] not in identities:
                identities.add(i["featuredMessage"]["url"])
                found += 1
                try:
                    i["address"]["line2"] = i["address"]["line2"]
                except Exception:
                    i["address"]["line2"] = ""
                yield i
        total += found
        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        logzilla.info(
            f"{zipcode} | found: {found} | total: {total} | progress: {progress}"
        )

    searchCA = DynamicZipSearch(
        country_codes=[SearchableCountries.CANADA],
        max_radius_miles=2500,
        max_search_results=50,
    )
    maxZ = searchCA.items_remaining()
    for zipcode in searchCA:
        if search.items_remaining() > maxZ:
            maxZ = searchCA.items_remaining()
        found = 0

        son = session.get(url + '"' + str(zipcode) + '"' + ext, headers=headers).json()

        for i in son["response"]["entities"]:
            search.found_location_at(
                i["yextDisplayCoordinate"]["latitude"],
                i["yextDisplayCoordinate"]["longitude"],
            )
            if i["featuredMessage"]["url"] not in identities:
                identities.add(i["featuredMessage"]["url"])
                found += 1
                try:
                    i["address"]["line2"] = i["address"]["line2"]
                except Exception:
                    i["address"]["line2"] = ""
                yield i
        total += found
        progress = str(round(100 - (searchCA.items_remaining() / maxZ * 100), 2)) + "%"
        logzilla.info(
            f"{zipcode} | found: {found} | total: {total} | progress: {progress}"
        )

    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def human_hours(k):
    h = []
    for i in list(k):
        if i == "reopenDate" or i == "holidayHours":
            continue
        try:
            k[i]["isClosed"] = k[i]["isClosed"]
        except Exception:
            k[i]["isClosed"] = False

        if k[i]["isClosed"]:
            h.append(i + ": Closed")
        else:
            hours = str(i) + ": "
            for j in k[i]["openIntervals"]:
                hours = hours + j["start"] + "-" + j["end"]
                if len(k[i]["openIntervals"]) > 1:
                    hours = hours + " & "
            if hours[-2] == "&":
                hours.pop(-2)
                hours = hours.strip()
            h.append(hours)
    return "; ".join(h)


def scrape():
    url = "https://www.gomongo.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["featuredMessage", "url"],
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["yextDisplayCoordinate", "latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["yextDisplayCoordinate", "longitude"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["address", "line1"], ["address", "line2"]],
            multi_mapping_concat_with=", ",
            value_transform=fix_comma,
        ),
        city=sp.MappingField(
            mapping=["address", "city"],
        ),
        state=sp.MappingField(
            mapping=["address", "region"],
        ),
        zipcode=sp.MappingField(
            mapping=["address", "postalCode"],
        ),
        country_code=sp.MappingField(
            mapping=["address", "countryCode"],
        ),
        phone=sp.MappingField(
            mapping=["mainPhone"],
        ),
        store_number=sp.MappingField(
            mapping=["meta", "id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hours"], raw_value_transform=human_hours
        ),
        location_type=sp.MappingField(
            mapping=["meta", "schemaTypes"], raw_value_transform=lambda x: ", ".join(x)
        ),
        raw_address=sp.MissingField(),
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
