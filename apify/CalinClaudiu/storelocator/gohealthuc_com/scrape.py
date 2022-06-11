from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape import sgpostal as parser


def f_adr(rec):
    MISSING = "<MISSING>"
    parsed = parser.parse_address_usa(str(rec["full_address"]).replace(",", "").strip())
    street_address = parsed.street_address_1 if parsed.street_address_1 else MISSING
    street_address = (
        (street_address + ", " + parsed.street_address_2)
        if parsed.street_address_2
        else street_address
    )
    rec["real_address"] = street_address
    return rec


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://www.gohealthuc.com/"
    with SgRequests() as session:
        res = SgRequests.raise_on_err(session.get(url))

        build_ID = res.text.split('"buildId":"', 1)[1].split('"', 1)[0]
        data_url = f"https://www.gohealthuc.com/_next/data/{build_ID}/locations.json"
        data = SgRequests.raise_on_err(session.get(data_url)).json()
        for record in data["pageProps"]["centers"]:
            yield f_adr(record)
    logzilla.info(f"Finished grabbing data!!")  # noqa


def human_hours(x):

    hours = []
    for i in x:
        hours.append(
            str(
                str(i["day_of_week"])
                + ": "
                + str(i["open_time"])
                + "-"
                + str(i["close_time"])
            )
        )

    return "; ".join(hours)


def scrape():
    url = "https://www.gohealthuc.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MultiMappingField(
            mapping=[
                ["jv"],
                ["uid"],
            ],
            multi_mapping_concat_with="/locations/",
            part_of_record_identity=True,
            value_transform=lambda x: "https://www.gohealthuc.com/" + x,
        ),
        location_name=sp.MappingField(
            mapping=["name"], value_transform=lambda x: x.replace("None", "<MISSING>")
        ),
        latitude=sp.MappingField(
            mapping=["coordinates", "latitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        longitude=sp.MappingField(
            mapping=["coordinates", "longitude"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        street_address=sp.MappingField(
            mapping=["real_address"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        city=sp.MappingField(
            mapping=["city"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        state=sp.MappingField(
            mapping=["state"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        zipcode=sp.MappingField(
            mapping=["zipCode"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        country_code=sp.MappingField(
            mapping=["time_zone"],
            value_transform=lambda x: x.split("/", 1)[0],
        ),
        phone=sp.MappingField(
            mapping=["phone_number"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        store_number=sp.MappingField(
            mapping=["id"],
            value_transform=lambda x: x.replace("None", "<MISSING>"),
        ),
        hours_of_operation=sp.MappingField(
            mapping=["hoursArr"], raw_value_transform=human_hours
        ),
        location_type=sp.MissingField(),
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
