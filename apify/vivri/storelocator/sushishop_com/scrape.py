from simple_scraper_pipeline import *
from simple_utils import *
import urllib.parse
import html.parser
import re
from functools import partial
import simple_network_utils
from bs4 import BeautifulSoup

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
    """
    The main entrypoint into the program.
    """

    fetch_data = lambda: simple_network_utils.fetch_xml(
        locations_url="https://sushishop.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php",
        query_params={
            "wpml_lang": "en",
            "t": str(ms_since_epoch)
        },
        headers={},
        data_params={},
        root_node_name="store",
        location_node_name="item",
        location_parser=xml_to_dict_one_level_deep
    )

    record_mapping = {
        "page_url": [["exturl"]],
        "location_name": [["location"]],
        "street_address": [["address"]],
        "city": [["address"]],
        "state": [["address"]],
        "zip": [["address"]],
        "store_number": [["storeid"]],
        "phone": [["telephone"]],
        "latitude": [["latitude"]],
        "longitude": [["longitude"]],
        "country_code": [["country"]],
        "hours_of_operation": [["operatinghours"]]
    }

    constant_fields = {
        "locator_domain": "https://sushishop.com",
        "location_type": "Sushi Shop Restaurant", # only one type of location
    }

    one_offs = lambda s: s\
        .replace("J4W 1 M7", "J4W 1M7")\
        .replace(",   J5T 2H5", ",QC, J5T 2H5") # missing province

    normalize_address_text =  partial(apply_in_seq, [massage_html_text, one_offs])

    extract_country_code_default_canada = partial(extract_country_code_common_n_a_mappings, "CA")

    field_transformers = {
        "street_address": partial(apply_in_seq, [normalize_address_text, extract_street_address]),
        "city": partial(apply_in_seq, [normalize_address_text, extract_city]),
        "state": partial(apply_in_seq, [normalize_address_text, extract_state]),
        "zip": partial(apply_in_seq, [normalize_address_text, extract_zip_postal]),
        "country_code": extract_country_code_default_canada,
        "hours_of_operation": partial(apply_in_seq, [massage_html_text, extract_hours]),
        "phone": partial(apply_in_seq, [massage_html_text, extract_first_phone]),
    }

    record_identity_fields = ["latitude", "longitude"]

    define_and_run( data_fetcher= fetch_data,
                    record_mapping=record_mapping,
                    constant_fields=constant_fields,
                    field_transform=field_transformers,
                    record_identity_fields=record_identity_fields,
                    fail_on_outlier=False,)

scrape()