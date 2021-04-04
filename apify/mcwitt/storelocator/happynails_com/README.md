``` shell
python validate.py data.csv --ignore GeoConsistencyValidator --ignore CountryValidator
```

Ignore flags necessitated by the following 2 problematic records returned by the API (note `state` and `zip`):

```json
[
    {
        "address": "2800 N. Main Street",
        "description": "",
        "store": "Happy Nails &#038; Spa of Main Place Mall",
        "thumb": "",
        "id": "1077",
        "distance": 6.9,
        "address2": "Suite 2084",
        "city": "Santa Ana",
        "state": "",
        "zip": "California",
        "country": "united states",
        "lat": "33.776896",
        "lng": "-117.870279",
        "phone": "(714) 541-6135",
        "fax": "",
        "email": "",
        "hours": "<table role=\"presentation\" class=\"wpsl-opening-hours\"><tr><td>Monday</td><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Tuesday</td><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Wednesday</td><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Thursday><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Friday</td><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Saturday</td><td><time>10:00 AM - 8:00 PM</time></td></tr><tr><td>Sunday</td><td><time>10:00 AM - 7:00 PM</time></td></tr></table>",
        "url": ""
    },
    {
        "address": "4735 Clairemont Dr, Suite #54",
        "description": "",
        "store": "Happy Nails and Spa Of Clairemont SQ",
        "thumb": "",
        "id": "1168",
        "distance": 71.1,
        "address2": "",
        "city": "San Diego",
        "state": "92117",
        "zip": "92117",
        "country": "united states",
        "lat": "32.830551",
        "lng": "-117.204731",
        "phone": "(619) 260-1764",
        "fax": "",
        "email": "",
        "hours": "<table role=\"presentation\" class=\"wpsl-opening-hours\"><tr><td>Monday</td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Tuesday</td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Wednesday</td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Thursday td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Friday</td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Saturday</td><td><time>10:00 AM - 9:00 PM</time></td></tr><tr><td>Sunday</td><td><time>11:00 AM - 7:00 PM</time></td></tr></table>",
        "url": ""
    }
]
 ```
