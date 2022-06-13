from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton
from bs4 import BeautifulSoup as b4
import json  # noqa
from sgscrape.sgrecord import SgRecord
from sgscrape import sgpostal as parser

logzilla = sglog.SgLogSetup().get_logger(logger_name="mani")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
}


def parse(data):
    soup = data[0]
    url = data[1]

    k = {}
    k["url"] = url
    try:
        k["name"] = soup.find(
            "h1",
            {
                "class": lambda x: x
                and all(i in x for i in ["Heading", "Hero-heading", "Heading--head"])
            },
        ).text.strip()
    except Exception as e:
        logzilla.error("name", exc_info=e)
        k["name"] = SgRecord.MISSING

    try:
        coords = soup.find(
            "span",
            {
                "class": "Address-coordinates",
                "itemtype": "http://schema.org/GeoCoordinates",
            },
        )
        k["lat"] = coords.find("meta", {"itemprop": "latitude"})["content"]
        k["lng"] = coords.find("meta", {"itemprop": "longitude"})["content"]
    except Exception as e:
        logzilla.error("coords", exc_info=e)
        k["lat"] = SgRecord.MISSING
        k["lng"] = SgRecord.MISSING

    try:
        k["address"] = soup.find(
            "span",
            {
                "class": lambda x: x
                and all(i in x for i in ["Address-field", "Address-line1"])
            },
        ).text.strip()
        try:
            k["address"] = (
                k["address"]
                + ", "
                + soup.find(
                    "span",
                    {
                        "class": lambda x: x
                        and all(i in x for i in ["Address-field", "Address-line2"])
                    },
                ).text.strip()
            )
        except Exception:
            pass
    except Exception as e:
        logzilla.error("address", exc_info=e)
        k["address"] = SgRecord.MISSING

    try:
        k["city"] = soup.find(
            "span",
            {
                "class": lambda x: x
                and all(i in x for i in ["Address-field", "Address-city"])
            },
        ).text.strip()
    except Exception as e:
        logzilla.error("city", exc_info=e)
        k["city"] = SgRecord.MISSING

    try:
        k["state"] = soup.find("meta", {"name": "geo.region", "content": True})[
            "content"
        ].split("-")[-1]
    except Exception as e:
        logzilla.error("state", exc_info=e)
        k["state"] = SgRecord.MISSING

    try:
        k["zip"] = soup.find(
            "span",
            {
                "class": lambda x: x
                and all(i in x for i in ["Address-field", "Address-postalCode"])
            },
        ).text.strip()
    except Exception as e:
        logzilla.error("zip", exc_info=e)
        k["zip"] = SgRecord.MISSING

    try:
        k["country"] = url.split("/")[4]
    except Exception:
        k["country"] = SgRecord.MISSING

    try:
        k["phone"] = soup.find(
            "a",
            {
                "data-ya-track": "phone",
                "class": lambda x: x and all(i in x for i in ["Link", "Phone-link"]),
            },
        )["href"]
        try:
            k["phone"] = k["phone"].split(":")[-1]
        except Exception:
            pass
    except Exception:
        k["phone"] = SgRecord.MISSING

    try:
        dat = soup.find(
            "a",
            {
                "data-ya-track": lambda x: x and "cta" in x,
                "class": lambda x: x
                and all(i in x for i in ["Button", "Hero-button", "Button--primary"]),
            },
        )["href"]
        try:
            k["country"] = dat.split("countryIso=", 1)[1].split("&", 1)[0]
        except Exception as e:
            logzilla.error(f"country_code {dat}", exc_info=e)
            if not dat:
                logzilla.error(f"\n\n\n\n\n\n\n\n\n\n{str(soup)}\n\n\n\n\n\n\n\n\n\n")
        try:
            k["id"] = dat.split("storeId=", 1)[1].strip()
        except Exception:
            k["id"] = SgRecord.MISSING

    except Exception:
        pass

    try:
        j = []
        k["hours"] = soup.find("div", {"data-days": True})["data-days"]
        k["hours"] = json.loads(k["hours"])
        for i in k["hours"]:
            if "rue" in str(i["isClosed"]):
                j.append(str(i["day"] + ": Closed"))
            else:
                j.append(
                    str(
                        i["day"]
                        + ": "
                        + str(
                            str(int(i["intervals"][0]["start"]) / 100)
                            + ":"
                            + str(int(i["intervals"][0]["start"]) % 100)
                        )
                        + "-"
                        + str(
                            str(int(i["intervals"][0]["end"]) / 100)
                            + ":"
                            + str(int(i["intervals"][0]["end"]) % 100)
                        )
                    )
                )
        k["hours"] = "; ".join(j)
    except Exception as e:
        logzilla.error("hours", exc_info=e)
        k["hours"] = SgRecord.MISSING

    try:
        rawa = soup.find("meta", {"itemprop": "streetAddress", "content": True})[
            "content"
        ]
    except Exception as e:
        logzilla.error("rawa", exc_info=e)
        rawa = None
    MISSING = SgRecord.Missing
    try:
        parsed = parser.parse_address_intl(rawa)
        street_address = parsed.street_address_1 if parsed.street_address_1 else MISSING
        street_address = (
            (street_address + ", " + parsed.street_address_2)
            if parsed.street_address_2
            else street_address
        )
        k["address"] = street_address
    except Exception as e:
        logzilla.error(f"Parsing\n{str(rawa)}", exc_info=e)

    return k


def grab_links(state):
    url = "https://stores.armaniexchange.com/"
    with SgRequests() as session:
        page = session.get(url)
        soup = b4(page.text, "lxml")
        continents = soup.find(
            "div",
            {
                "class": lambda x: x
                and all(i in x for i in ["Directory-groups", "l-row"])
            },
        ).find_all("a", {"href": True, "data-ya-track": "todirectory"})

        countries = continents
        for country in countries:
            if country["href"].count("/") > 0:
                state.push_request(SerializableRequest(url=country["href"]))
            else:
                page = session.get(url + country["href"])
                soup = b4(page.text, "lxml")
                stores = soup.find(
                    "section",
                    {
                        "class": lambda x: x
                        and all(
                            i in x
                            for i in ["Directory", "Directory--ace", "LocationList"]
                        )
                    },
                )
                stores = stores.find_all(
                    "a",
                    {
                        "href": True,
                        "data-ya-track": "details",
                        "class": lambda x: x
                        and all(
                            i in x
                            for i in [
                                "Link",
                                "Teaser-link",
                                "Teaser-ctaLink",
                                "Link--small",
                            ]
                        ),
                    },
                )
                for store in stores:
                    logzilla.info(f"{store['href']}")
                    state.push_request(SerializableRequest(url=store["href"]))

    return True


def fetch_stores(state):
    with SgRequests() as session:
        url_to_test = "https://stores.armaniexchange.com/united-kingdom/ax-armani-exchange-westfield-stratford-city"
        logzilla.info(
            f"{parse((b4(session.get(url_to_test).text,'lxml'),url_to_test))}"
        )
        for next_r in state.request_stack_iter():
            logzilla.info(str("https://stores.armaniexchange.com/" + next_r.url))
            try:
                res = SgRequests.raise_on_err(
                    session.get("https://stores.armaniexchange.com/" + next_r.url)
                )
            except Exception as e:
                if "520" or "404" in str(e):
                    try:
                        res = SgRequests.raise_on_err(
                            session.get(
                                "https://stores.armaniexchange.com/" + next_r.url
                            )
                        )
                    except Exception:
                        continue
                else:
                    raise Exception
            yield parse(
                (
                    b4(res.text, "lxml"),
                    str("https://stores.armaniexchange.com/" + next_r.url),
                )
            )


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    state.get_misc_value("init", default_factory=lambda: grab_links(state))
    state.save(override=True)
    for store in fetch_stores(state):
        yield store


def scrape():
    url = "https://armaniexchange.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["url"], part_of_record_identity=True),
        location_name=MappingField(mapping=["name"], is_required=False),
        latitude=MappingField(mapping=["lat"], is_required=False),
        longitude=MappingField(mapping=["lng"], is_required=False),
        street_address=MappingField(mapping=["address"], is_required=False),
        city=MappingField(mapping=["city"], is_required=False),
        state=MappingField(mapping=["state"], is_required=False),
        zipcode=MappingField(mapping=["zip"], is_required=False),
        country_code=MappingField(mapping=["country"], is_required=False),
        phone=MappingField(mapping=["phone"], is_required=False),
        store_number=MappingField(
            mapping=["id"], is_required=False, part_of_record_identity=True
        ),
        hours_of_operation=MappingField(mapping=["hours"], is_required=False),
        location_type=MappingField(mapping=["type"], is_required=False),
        raw_address=MappingField(mapping=["rawa"], is_required=False),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="armaniexchange.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=25,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
