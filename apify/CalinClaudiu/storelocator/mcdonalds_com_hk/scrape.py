from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from sgpostal.sgpostal import parse_address_intl

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def OneLink():
    def getPage():
        url = "https://www.mcdonalds.com.hk/wp-admin/admin-ajax.php?action=get_restaurants"
        data = "type=init"
        headers = {}
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        with SgRequests() as session:
            response = session.post(url, headers=headers, data=data)
            return response.json()

    def record_cleaner(record):
        parsed = parse_address_intl(record["address"])
        record["country"] = parsed.country if parsed.country else "<MISSING>"
        record["state"] = parsed.state if parsed.state else "<MISSING>"
        record["city"] = parsed.city if parsed.city else "<MISSING>"
        record["zipcode"] = parsed.postcode if parsed.postcode else "<MISSING>"
        record["address"] = parsed.street_address_1
        if parsed.street_address_2:
            record["address"] = record["address"] + " " + parsed.street_address_2
        return record

    data = getPage()
    if data:
        try:
            for records in data["restaurants"]:
                record = record_cleaner(records)
                yield record
        except Exception as e:
            logzilla.info(f"Had issues, issue:\n{str(e)}")


def fetch_data():
    for rec in OneLink():
        yield rec
    logzilla.info(f"Finished grabbing data!!")  # noqa


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h).replace("  ", " ")
    except Exception:
        return x.replace("  ", " ")


def scrape():
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField("mcdonalds.com.hk"),
        page_url=sp.MissingField(),
        location_name=sp.MappingField(
            mapping=["title"],
            is_required=False,
            part_of_record_identity=True,
        ),
        latitude=sp.MappingField(
            mapping=["lat"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        longitude=sp.MappingField(
            mapping=["lng"],
            is_required=False,
            value_transform=lambda x: x.replace("None", "<MISSING>"),
            part_of_record_identity=True,
        ),
        street_address=sp.MappingField(mapping=["address"], is_required=False),
        city=sp.MappingField(mapping=["city"], is_required=False),
        state=sp.MappingField(mapping=["state"], is_required=False),
        zipcode=sp.MappingField(mapping=["zipcode"], is_required=False),
        country_code=sp.MappingField(mapping=["country"], is_required=False),
        phone=sp.MappingField(
            mapping=["telephone"],
            is_required=False,
        ),
        store_number=sp.MissingField(),
        hours_of_operation=sp.MissingField(),
        location_type=sp.MappingField(mapping=["tooltips"], is_required=False),
        raw_address=sp.MissingField(),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5000,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
