"""
Simple network utilities
"""
from simple_utils import *
from sgrequests import SgRequests
import bs4
import urllib.parse
from bs4 import BeautifulSoup
import simplejson as json
from requests_toolbelt.utils import dump

def fetch_json(locations_url: str,
              query_params: dict,
              data_params: dict,
              headers: dict,
              path_to_locations: List[str]) -> List[Dict[str, str]]:

    response = fetch_data(locations_url=locations_url, data_params=data_params, query_params=query_params,headers=headers)

    json_result = json.loads(urllib.parse.unquote(response.text), encoding="utf8")

    drill_down_into(json_result, path_to_locations)

    return json_result['data']['result_list']

def fetch_xml(locations_url: str,
              query_params: dict,
              data_params: dict,
              headers: dict,
              root_node_name: str,
              location_node_name: str,
              location_parser: Callable[[bs4.Tag], Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Fetches locations xml, and returns as a list of parsed dictionaries.
    Assumes a regular structure with root element, and sibling-elements.

    :param data_params: raw (non-urlencoded) data parameters as a dict.
    :param locations_url: The url of the xml.
    :param query_params: raw (non-urlencoded) queryparams.
    :param headers: query headers.
    :param root_node_name: root element under which locations are stored.
    :param location_node_name: element name of each location.
    :param location_parser: function that converts a location Tag into a dict.
    :return: a list of parsed dictionaries
    """

    response = fetch_data(locations_url=locations_url, data_params=data_params, query_params=query_params,headers=headers)

    xml_result = BeautifulSoup(response.text, 'lxml')

    root_node = xml_result.find(root_node_name)

    location_nodes = root_node.find_all(location_node_name)

    data = []
    for location in location_nodes:
        data.append(location_parser(location))

    return data

def fetch_data(locations_url: str,
              query_params: dict,
              data_params: dict,
              headers: dict):
    session = SgRequests()

    response = session.get(locations_url, data=urllib.parse.urlencode(data_params), params=urllib.parse.urlencode(query_params), headers=headers)

    if response.status_code < 200 or response.status_code > 299:
        stderr("API call is not successful; result status: " + str(response.status_code))
        stderr(dump.dump_all(response).decode("utf-8"))
        raise Exception("API call is not successful; result status: " + str(response.status_code))

    return response