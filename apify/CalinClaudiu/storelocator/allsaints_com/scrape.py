from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog

from sgscrape import simple_utils as utils
from sgscrape import sgpostal as parser
import re
from sgrequests import SgRequests


def determine_location(record):
    def determine_images(percent):
        return [lambda: percent, lambda: percent * 7][bool(record["images"])]()

    def determine_about(percent):
        return [
            lambda: determine_images(percent),
            lambda: determine_images(percent * 5),
        ][bool(record["about"])]()

    def determine_attributes(percent):
        return [lambda: determine_about(percent), lambda: determine_about(percent * 3)][
            bool(record["attributes"])
        ]()

    return [lambda: determine_attributes(0), lambda: determine_attributes(11)][
        bool(re.match(r"^[A-Z0-9\-]+$", record["slug"]))
    ]()


def para(record):
    url = "https://store-locator-api.allsaints.com/{country_slug}/{city_slug}/{slug}"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(
        url.format(
            country_slug=record["country_slug"],
            city_slug=record["city_slug"],
            slug=record["slug"],
        ),
        headers=headers,
    ).json()
    session.close()
    son["page_url_post"] = url.format(
        country_slug=record["country_slug"],
        city_slug=record["city_slug"],
        slug=record["slug"],
    )

    son["raw"] = (
        str(son["address_line1"])
        + " "
        + str(son["address_line2"])
        + " "
        + str(son["address_line3"])
        + " "
        + str(son["city"])
        + " "
        + str(son["post_code"])
    )
    parsed = parser.parse_address_intl(
        son["raw"].replace("None", "").replace("  ", " ")
    )
    son["parsedaddress"] = (
        parsed.street_address_1 if parsed.street_address_1 else "<MISSING>"
    )
    son["parsedaddress"] = (
        (son["parsedaddress"] + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else son["parsedaddress"]
    )
    son["parsedCity"] = parsed.city if parsed.city else "<MISSING>"
    son["parsedState"] = parsed.state if parsed.state else "<MISSING>"
    son["parsedpost_code"] = parsed.postcode if parsed.postcode else "<MISSING>"

    son["locationType"] = str(determine_location(son)).replace("0", "<MISSING>")
    return son


def fetch_data():
    # print(para({"country_slug":"usa","city_slug":"honolulu","slug":"NA-US-1-072"})) # noqa
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://store-locator-api.allsaints.com/shops"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers).json()
    session.close()
    lize = utils.parallelize(
        search_space=son,
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=10,
    )
    for i in lize:
        yield i

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


def human_hours(raw):
    hours = []
    for i in list(raw):
        for j in raw[i]:
            hours.append(
                str(
                    str(i)
                    + ": "
                    + str(j["open"]).replace("None", "Closed")
                    + "-"
                    + str(j["close"]).replace("None", "Closed")
                ).replace("Closed-Closed", "Closed")
            )
    return "; ".join(hours)


def onlydigits(x):
    new = []
    for i in x:
        if i.isdigit():
            new.append(i)
    if len(new) < 3:
        return "<MISSING>"
    return "".join(new)


def scrape():
    url = "www.allsaints.com"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["page_url_post"],
            part_of_record_identity=True,
        ),
        location_name=sp.MappingField(
            mapping=["name"],
        ),
        latitude=sp.MappingField(
            mapping=["coordinates", "latitude"],
        ),
        longitude=sp.MappingField(
            mapping=["coordinates", "longitude"],
        ),
        street_address=sp.MappingField(mapping=["parsedaddress"]),
        city=sp.MappingField(
            mapping=["parsedCity"],
        ),
        state=sp.MappingField(
            mapping=["parsedState"],
        ),
        zipcode=sp.MappingField(
            mapping=["parsedpost_code"],
        ),
        country_code=sp.MappingField(
            mapping=["country"],
        ),
        phone=sp.MappingField(
            mapping=["phone_number"],
            part_of_record_identity=True,
            value_transform=onlydigits,
        ),
        store_number=sp.MappingField(
            mapping=["uuid"],
            part_of_record_identity=True,
        ),
        hours_of_operation=sp.MappingField(
            mapping=["opening_hours"],
            raw_value_transform=human_hours,
        ),
        location_type=sp.MappingField(
            mapping=["locationType"], value_transform=lambda x: "<MISSING>"
        ),
        raw_address=sp.MappingField(
            mapping=["raw"],
            part_of_record_identity=True,
        ),
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
