from sgscrape import simple_scraper_pipeline as sp
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


#https://mcdonalds.co.kr/kor/store/list.do?page=81&lat=NO&lng=NO&search_options=&searchWord=
#Road in thing means results

def cleanup_this(raw):
    clean = {}
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = ""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    
    with session as SgRequests():
        url = "https://mcdonalds.co.kr/kor/store/list.do?page={}&lat=NO&lng=NO&search_options=&searchWord="
        page = 1
        while True:
            dat = session.post(url.format(page), headers=headers).text
            soup = b4(dat, "lxml")
            if '"road"' not in dat:
                break
            data = soup.find("table",{"class":"tableType01"}).find('tbody').find_all('tr')
            for raw in data:
                yield cleanup_this(raw)

    logzilla.info(f"Finished grabbing data!!")  # noqa

def fix_comma(x):
    h = []
    try:
        for i in x.split(','):
            if len(i.strip())>=1:
                h.append(i)
        return ', '.join(h)
    except Exception:
        return x
  
def scrape():
    url = ""
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        location_name=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        latitude=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        longitude=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        street_address=sp.MultiMappingField(
            mapping=[["xxxxxxxxx"], ["xxxxxxxxx"]],
            multi_mapping_concat_with = ", ",
            value_transform = fix_comma,
        ),
        city=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        state=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        zipcode=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        country_code=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        phone=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        store_number=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        hours_of_operation=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
        ),
        location_type=sp.MissingField(),
        raw_address=sp.MappingField(
            mapping=["xxxxxxxxxxxxxxxxxxx"],
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
