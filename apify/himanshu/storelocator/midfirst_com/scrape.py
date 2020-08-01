import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import sgzip



session = SgRequests()

    driver = SgSelenium().firefox()
