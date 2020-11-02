import urllib.parse
import html.parser
import re
from functools import partial

from sgscrape.simple_utils import *
from sgscrape.simple_network_utils import *
from sgscrape.simple_scraper_pipeline import *

comma_regex = re.compile(r',')
postal_regex_str = r'[A-Z]\d[A-Z] ?\d[A-Z]\d'
zip_regex_str = r'\d{5}(?:-\d{4})?'
zip_postal_regex_str = fr'({postal_regex_str}|{zip_regex_str})'
zip_postal_regex = re.compile(fr"(.+){zip_postal_regex_str}")

def massage_html_text(s: str) -> str:
    unquoted: str = urllib.parse.unquote(s)
    return html.parser.unescape(unquoted)\
        .replace("\r\n", " ")\
        .replace("\n", " ")\
        .replace(chr(160), " ")

def split_address_no_zip(s: str):
    fields = comma_regex.split(zip_postal_regex.match(s).group(1))
    ret = []
    for f in fields:
        stripped = f.strip()
        if stripped != "":
            ret.append(stripped)
    return ret

def extract_street_address(s: str) -> str:
    addr_no_zip = split_address_no_zip(s)
    last_street_address_part_with_maybe_city = addr_no_zip[len(addr_no_zip)-2].split(" ")
    last_street_address_part = last_street_address_part_with_maybe_city[0:len(last_street_address_part_with_maybe_city)-1]

    addr_no_zip_updated = addr_no_zip[0:len(addr_no_zip)-2]
    addr_no_zip_updated.extend(last_street_address_part)

    return merge_ar(addr_no_zip_updated, ", ")

def extract_city(s: str) -> str:
    addr_no_zip = split_address_no_zip(s)
    city_with_maybe_some_street_address = addr_no_zip[len(addr_no_zip)-2].split(" ")
    return city_with_maybe_some_street_address[len(city_with_maybe_some_street_address)-1]

def extract_state(s: str) -> str:
    addr_no_zip = split_address_no_zip(s)
    return addr_no_zip[len(addr_no_zip)-1].strip()

def extract_zip_postal(s: str) -> str:
    return zip_postal_regex.match(s).group(2)

def extract_hours(s: str) -> str:
    if s.find("Closed temporarily") is not -1:
        return MISSING
    else:
        hours_html = BeautifulSoup(s, "lxml")
        hours = []
        for hour_node in hours_html.find_all("p", {"class": "MsoNormal"}):
            hours.append(hour_node.text.replace('\n', ' ').strip())

        # fun stuff: we also have hours as divs after the initial "selected" `p`!
        for hour_node in hours_html.find_all("div"):
            hours.append(hour_node.text.replace('\n', ' ').strip())

        return merge_ar(hours, " ; ")

def extract_first_phone(s: str) -> str:
    return s.split(",")[0]

def scrape():

    fetch_data_fn = lambda: fetch_xml(
        request_url="https://sushishop.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",
        query_params={
            "wpml_lang": "en",
            "t": str(ms_since_epoch)
        },
        root_node_name="store",
        location_node_name="item",
        location_parser=xml_to_dict_one_level_deep
    )

    one_offs = lambda s: s \
        .replace("J4W 1 M7", "J4W 1M7") \
        .replace(",   J5T 2H5", ",QC, J5T 2H5")  # missing province

    normalize_address_text = partial(apply_in_seq, [massage_html_text, one_offs])

    extract_country_code_default_canada = partial(extract_country_code_common_n_a_mappings, "CA")

    street_addr_transform = partial(apply_in_seq, [normalize_address_text, extract_street_address])
    city_transform = partial(apply_in_seq, [normalize_address_text, extract_city])
    state_transform = partial(apply_in_seq, [normalize_address_text, extract_state])
    zip_transform = partial(apply_in_seq, [normalize_address_text, extract_zip_postal])
    country_code_transform = extract_country_code_default_canada
    hours_operation_transform = partial(apply_in_seq, [massage_html_text, extract_hours])
    phone_transform = partial(apply_in_seq, [massage_html_text, extract_first_phone])

    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField("https://sushishop.com"),
        page_url=MappingField(mapping=["exturl"], is_required=False),
        location_name=MappingField(mapping=["location"]),
        street_address=MappingField(mapping=["address"], value_transform=street_addr_transform),
        city=MappingField(mapping=["address"], value_transform=city_transform),
        state=MappingField(mapping=["address"], value_transform=state_transform),
        zipcode=MappingField(mapping=["address"], value_transform=zip_transform),
        country_code=MappingField(mapping=["country"], value_transform=country_code_transform),
        store_number=MappingField(mapping=["storeid"]),
        phone=MappingField(mapping=["telephone"], value_transform=phone_transform, is_required=False),
        location_type=MissingField(),
        latitude=MappingField(mapping=["latitude"], part_of_record_identity=True),
        longitude=MappingField(mapping=["longitude"], part_of_record_identity=True),
        hours_of_operation=MappingField(mapping=["operatinghours"], value_transform=hours_operation_transform, is_required=False)
    )

    pipeline = SimpleScraperPipeline(scraper_name="sushishop.com",
                                     data_fetcher= fetch_data_fn,
                                     field_definitions=field_defs,
                                     fail_on_outlier=False)

    pipeline.run()

if __name__ == "__main__":
    scrape()