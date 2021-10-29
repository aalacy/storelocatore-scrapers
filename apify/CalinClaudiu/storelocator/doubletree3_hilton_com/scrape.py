from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sglogging import sglog
from sgscrape.pause_resume import SerializableRequest, CrawlStateSingleton


from sgscrape import simple_utils as utils  # noqa


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json
import time
from sgselenium import SgChrome

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def cleanup_json(x, url):
    try:
        z = x.split('"description"')[0] + str('"opening') + x.split('"opening', 1)[1]
    except Exception as e:
        logzilla.error(f"{x}\n{str(e)}\n{str(url)}")
        z = x
    x = z
    x = x.replace("\n", "").replace("\r", "").replace("\t", "")
    x = x.replace(": '", ': "')
    x = x.replace("',", '",')
    x = x.replace("' }", '" }').replace("'}", '"}')
    copy = []
    i = 0
    length = len(x)
    while i < length:
        if x[i] != "<":
            copy.append(x[i])
        else:
            while x[i] != ">":
                i = i + 1
        i += 1
    x = "".join(copy)
    x = x.replace(",}}", "}}")
    try:
        x = json.loads(x)
    except Exception as e:
        with open("debug.txt", mode="w", encoding="utf-8") as file:
            file.write(x)
            file.write(str(e))
            file.write(str(url))
        logzilla.error(f"{x}\n{str(e)}\n{str(url)}")
    return x


def para(k, session):

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    son = None
    try:
        son = SgRequests.raise_on_err(
            session.get(
                k["facilityOverview"]["homeUrl"].replace("https", "http"),
                headers=headers,
            )
        )
    except Exception as e:
        try:
            logzilla.error(f"{str(e)}\n{k['facilityOverview']['homeUrl']}\n\n")
        except Exception as feck:
            logzilla.error(f"{str(feck)}\n{k}\n\n")
    try:

        soup = b4(son.text, "lxml")

        allscripts = soup.find_all("script", {"type": "application/ld+json"})
    except Exception:
        pass

    data = {}
    k["extras"] = {}
    k["extras"]["address"] = {}
    k["extras"]["address"]["postalCode"] = "<MISSING>"
    try:
        for i in allscripts:
            if "postalCode" in i.text:
                try:
                    z = i.text.replace("\n", "")
                    data = cleanup_json(z, k["facilityOverview"]["homeUrl"])
                except Exception:
                    raise
    except Exception:
        pass
    try:
        k["extras"] = data
    except Exception:
        k["extras"]["address"]["postalCode"] = "<MISSING>"
        k["extras"]["openingHours"] = "<MISSING>"

    return k


def gen_countries(session):
    url = "https://www.hilton.com/en/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    main = session.get(url, headers=headers)
    soup = b4(main.text, "lxml")
    countries = []
    data = soup.find_all(
        "div",
        {
            "id": lambda x: x and "location-tab-panel-" in x,
            "aria-labelledby": lambda x: x and "location-tab" in x,
            "role": "tabpanel",
            "tabindex": True,
            "class": True,
        },
    )
    for alist in data:
        links = alist.find_all("a")
        for link in links:
            countries.append(
                {
                    "text": link.text,
                    "link": link["href"].replace("https", "http"),
                    "complete": False,
                }
            )
    return countries


def fetch_data():
    state = CrawlStateSingleton.get_instance()
    with SgRequests(verify_ssl=False) as session:
        countries = state.get_misc_value(
            "countries", default_factory=lambda: gen_countries(session)
        )
        for country in countries:
            if not country["complete"]:
                try:
                    data_fetcher(country, state, 10)
                except Exception as e:
                    logzilla.error(f"{str(country)}\n{str(e)}")
                country["complete"] = True
                state.set_misc_value("countries", countries)
            for next_r in state.request_stack_iter():
                yield para(next_r.context, session)


def data_fetcher(country, state, sleep):
    url = country["link"]
    masterdata = []
    with SgChrome() as driver:
        driver.get(url.replace("https", "http"))
        time.sleep(sleep)
        for r in driver.requests:
            data = None
            if "graphql/customer" in r.path:
                try:
                    if r.response.body:
                        data = r.response.body
                        data = json.loads(data)
                        masterdata.append(data)
                    else:
                        time.sleep(30)
                except AttributeError:
                    try:
                        time.sleep(30)
                        if r.response.body:
                            data = r.response.body
                            data = json.loads(data)
                            masterdata.append(data)
                        else:
                            time.sleep(30)
                    except AttributeError:
                        try:
                            time.sleep(30)
                            if r.response.body:
                                data = r.response.body
                                data = json.loads(data)
                                masterdata.append(data)
                        except Exception:
                            pass
    total = 0
    allhotels = []
    if len(masterdata) == 0:
        sleep += 10
        if sleep < 30:
            return data_fetcher(country, state, sleep)
    for i in masterdata:
        try:
            total = total + len(i["data"]["hotelSummaryOptions"]["hotels"])
            for j in i["data"]["hotelSummaryOptions"]["hotels"]:
                allhotels.append(j)
        except KeyError as e:
            logzilla.error(f"{str(i)[:200]}\n{str(e)}\n\n")

    logzilla.info(f"Found a total of {total} hotels for country {country}")  # noqa
    for req in allhotels:
        state.push_request(SerializableRequest(url="<MISSING>", context=req))

    logzilla.info(f"Finished grabbing data!!")  # noqa


def scrape():
    url = "https://www.hilton.com/en/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["facilityOverview", "homeUrl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(
            mapping=["localization", "coordinate", "latitude"],
        ),
        longitude=MappingField(
            mapping=["localization", "coordinate", "longitude"],
        ),
        street_address=MappingField(
            mapping=["address", "addressLine1"], part_of_record_identity=True
        ),
        city=MappingField(mapping=["address", "city"]),
        state=MappingField(
            mapping=["address", "state"],
            value_transform=lambda x: x.replace("None", "<MISSING>").replace(
                "Null", "<MISSING>"
            ),
        ),
        zipcode=MappingField(
            mapping=["extras", "address", "postalCode"], is_required=False
        ),
        country_code=MappingField(mapping=["address", "country"]),
        phone=MappingField(
            mapping=["contactInfo", "phoneNumber"], part_of_record_identity=True
        ),
        store_number=MappingField(mapping=["_id"], part_of_record_identity=True),
        hours_of_operation=MappingField(
            mapping=["extras", "openingHours"],
            value_transform=lambda x: "Possibly Closed"
            if x == "FALSE"
            else "<MISSING>",
        ),
        location_type=MappingField(mapping=["brandCode"]),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=5,
        duplicate_streak_failure_factor=250,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
