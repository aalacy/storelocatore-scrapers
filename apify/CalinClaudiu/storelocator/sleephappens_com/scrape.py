from sgscrape.simple_scraper_pipeline import SimpleScraperPipeline
from sgscrape.simple_scraper_pipeline import ConstantField
from sgscrape.simple_scraper_pipeline import MappingField
from sgscrape.simple_scraper_pipeline import MissingField
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="sleephappens")
    url = "https://code.metalocator.com/index.php?user_lat=0&user_lng=0&postal_code=89117&radius=124124&Itemid=11139&view=directory&layout=combined&tmpl=component&framed=1&parent_table=&parent_id=0&task=search_zip&search_type=point&_opt_out=&option=com_locator&ml_location_override="
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    son = session.get(url, headers=headers)
    soup = BeautifulSoup(son.text, "lxml")
    soup = soup.find_all("script", {"type": "text/javascript", "language": False})
    for i in soup:
        if "jqLocator(document).ready(function()" in str(i):
            son = json.loads(
                str(
                    str(i)
                    .split("location_data", 1)[1]
                    .split("=", 1)[1]
                    .split("searchcenter", 1)[0]
                    .rsplit(";", 1)[0]
                )
            )
            found = []
            for i in son:
                if "closed" in i["name"].lower():
                    continue
                try:
                    i["country"] = i["country"]
                except:
                    i["country"] = "US"
                try:
                    i["link"] = i["websiteurl"]
                    if i["link"] in found:
                        continue
                    found.append(i["link"])
                except:
                    i["link"] = "<MISSING>"
                try:
                    i["phone"] = i["phone"]
                except:
                    if i["link"] != "<MISSING>":
                        req = session.get(i["websiteurl"], headers=headers)
                        base = BeautifulSoup(req.text, "lxml")
                        i["phone"] = base.find(class_="phone-text").text
                    else:
                        i["phone"] = "<MISSING>"
                try:
                    i["hours"] = i["hours"]
                except:
                    i["hours"] = (
                        "Sun "
                        + i["hourssunday"]
                        + " Mon "
                        + i["hoursmonday"]
                        + " Tue "
                        + i["hourstuesday"]
                        + " Wed "
                        + i["hourswednesday"]
                        + " Thu "
                        + i["hoursthursday"]
                        + " Fri "
                        + i["hoursfriday"]
                        + " Sat "
                        + i["hourssaturday"]
                    )
                yield i
    logzilla.info(f"Finished grabbing data!!")  # noqa


def pretty_hours(x):
    if "{" in x:
        x = x.replace("{", "")
        x = x.split("}")
        try:
            x.pop(-1)
            x.pop(-1)
            x = "; ".join(x)
        except:
            x = "Closed"
    return x


def scrape():
    url = "https://stores.sleephappens.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=["websiteurl"]),
        location_name=MappingField(mapping=["name"]),
        latitude=MappingField(mapping=["lat"]),
        longitude=MappingField(mapping=["lng"]),
        street_address=MappingField(mapping=["address"]),
        city=MappingField(mapping=["city"]),
        state=MappingField(mapping=["state"]),
        zipcode=MappingField(mapping=["postalcode"]),
        country_code=MappingField(mapping=["country"]),
        phone=MappingField(mapping=["phone"]),
        store_number=MappingField(mapping=["id"]),
        hours_of_operation=MappingField(
            mapping=["hours"], value_transform=pretty_hours
        ),
        location_type=MissingField(),
    )

    pipeline = SimpleScraperPipeline(
        scraper_name="stores.sleephappens.com",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=15,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
