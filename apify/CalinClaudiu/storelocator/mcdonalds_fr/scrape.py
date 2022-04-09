from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests


def grab_page(session, pageno):

    url = "https://api.woosmap.com/stores/?key=woos-77bec2e5-8f40-35ba-b483-67df0d5401be&page={}".format(
        pageno
    )

    headers = {}
    headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
    headers["cache-control"] = "no-cache"
    headers["origin"] = "https://www.restaurants.mcdonalds.fr"
    headers["pragma"] = "no-cache"
    headers["referer"] = "https://www.restaurants.mcdonalds.fr/"
    headers[
        "sec-ch-ua"
    ] = '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"'
    headers["sec-ch-ua-mobile"] = "?0"
    headers["sec-ch-ua-platform"] = '"Windows"'
    headers["sec-fetch-dest"] = "empty"
    headers["sec-fetch-mode"] = "cors"
    headers["sec-fetch-site"] = "cross-site"
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"

    return SgRequests.raise_on_err(session.get(url, headers=headers)).json()


def test_zipcode(item):
    if (
        not item["properties"]["address"]["zipcode"]
        or "one" in item["properties"]["address"]["zipcode"]
        or "ull" in item["properties"]["address"]["zipcode"]
    ):
        try:
            item["properties"]["address"]["zipcode"] = item["properties"][
                "user_properties"
            ]["displayPostCode"]
        except Exception:
            pass
    return item


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")

    with SgRequests(proxy_country="fr") as session:

        page = 1
        data = grab_page(session, page)
        maxpage = data["pagination"]["pageCount"]
        page += 1
        for item in data["features"]:
            yield item
        while page <= maxpage:
            data = grab_page(session, page)
            for item in data["features"]:
                yield test_zipcode(item)
            page += 1
    logzilla.info(f"Finished grabbing data!!")  # noqa


def pretty_hours(k):
    dotw = ["Mo", "Tu", "Wed", "Thu", "Fr", "Sat", "Sun"]
    hours = []
    for i in range(1, 8):
        daystring = str(dotw[i - 1]) + ": "
        for interval in k[str(i)]:
            try:
                daystring = daystring + str(
                    interval["start"] + "-" + interval["end"] + " "
                )
            except KeyError:
                if "all-day" in str(interval):
                    daystring = daystring + "24hours"
            hours.append(daystring)
    return "; ".join(hours)


def scrape():
    url = "mcdonalds.fr"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["properties", "contact", "website"],
            value_transform=lambda x: "https://www.restaurants.mcdonalds.fr/" + x,
        ),
        location_name=sp.MappingField(
            mapping=["properties", "name"],
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["geometry", "coordinates", 1],
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["geometry", "coordinates", 0],
        ),
        street_address=sp.MappingField(
            mapping=["properties", "address", "lines"],
            raw_value_transform=lambda x: ", ".join(x),
        ),
        city=sp.MappingField(
            mapping=["properties", "address", "city"],
            is_required=False,
        ),
        state=sp.MissingField(),
        zipcode=sp.MappingField(
            mapping=["properties", "address", "zipcode"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=sp.MappingField(
            mapping=["properties", "address", "country_code"],
            is_required=False,
        ),
        phone=sp.MappingField(
            mapping=["properties", "contact", "phone"],
            part_of_record_identity=True,
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        store_number=sp.MappingField(
            mapping=["properties", "store_id"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["properties", "opening_hours", "usual"],
            part_of_record_identity=True,
            is_required=False,
            raw_value_transform=pretty_hours,
        ),
        location_type=sp.MappingField(
            mapping=["properties", "tags"], value_transform=lambda x: str(x)
        ),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=55,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
