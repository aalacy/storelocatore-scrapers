from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from bs4 import BeautifulSoup as b4
from sgrequests import SgRequests
import json


def fetch_data():

    with SgRequests() as session:
        url = "https://locations.geisinger.org/?utm_source=Locations%20Page&utm_medium=Web&utm_campaign=Locations%20CTA"
        soup = session.get(url)
        # json location
        soup = b4(soup.text, "lxml")
        k = soup.find("div", {"id": "bottom"}).find("script").text.strip()
        k = k.split("var results= ")[1]
        k = k.split("[", 1)[1]
        k = k.split("}];")[0]
        k = '{"stores":[' + k + "}]}"
        son = json.loads(k)
        for i in son["stores"]:
            soup = session.get(
                str(
                    "https://locations.geisinger.org/details.cfm?id="
                    + str(i["CLINICID"])
                )
            )

            soup = b4(soup.text, "lxml")
            try:
                i["hours"] = "; ".join(
                    list(
                        soup.find("div", {"class": "officeHours"})
                        .find("p")
                        .stripped_strings
                    )
                )
            except Exception:
                try:
                    i["hours"] = "; ".join(
                        list(
                            soup.find("div", {"class": "officeHours"}).stripped_strings
                        )
                    )
                except Exception:
                    try:
                        i["hours"] = soup.find(
                            "div", {"class": "officeHours"}
                        ).text.strip()
                    except Exception:
                        i["hours"] = "<MISSING>"

            try:
                coords = soup.find("", {"href": lambda x: x and "maps" in x})["href"]
                coords = coords.split("/@", 1)[1].split("/", 1)[0].split(",")
            except Exception:
                coords = ["<MISSING>", "<MISSING>"]
            i["lon"] = coords[1]
            i["lat"] = coords[0]
            yield i


def parse_features(x):
    s = b4(str(x), "lxml")
    return "; ".join(list(s.stripped_strings))


def scrape():
    url = "https://www.geisinger.org/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(
            mapping=["CLINICID"],
            value_transform=lambda x: "https://locations.geisinger.org/details.cfm?id="
            + str(x),
        ),
        location_name=MappingField(
            mapping=["NAME"], value_transform=lambda x: x.replace("&amp; ", "")
        ),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lat"]),
        street_address=MappingField(mapping=["ADDRESS1"]),
        city=MappingField(mapping=["CITY"]),
        state=MappingField(mapping=["STATE"]),
        zipcode=MappingField(
            mapping=["ZIPCODE"],
            value_transform=lambda x: x.replace(" ", ""),
            is_required=False,
        ),
        country_code=MissingField(),
        phone=MappingField(mapping=["PHONE"], is_required=False),
        store_number=MappingField(mapping=["CLINICID"]),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(
            mapping=["OTHERSERVICES"], value_transform=parse_features, is_required=False
        ),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="scr",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
