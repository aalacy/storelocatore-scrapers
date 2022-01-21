# Using SgPostal

#### Library version:

```
sgpostal>=0.1.0
```

## What is it for?

- This library helps parse and normalize raw address strings, such as `123 Home ave. Cityville Ontario Canada`.

## Features

- Uses state of the art address-parsing and normalization libraries under the hood:
  - [pypostal](https://github.com/openvenues/pypostal) for international addresses.
  - [usaddress-scourgify](https://github.com/GreenBuildingRegistry/usaddress-scourgify), for US addresses.
- Chains and overlays library outputs where it makes sense.
- Has an additional layer of normalization and heuristics on top of said libraries to deal with most usecases.
- Returns structured, normalized data.

## Prerequisites

- Installing `libpostal` on your machine to allow for local running/debugging.
  - See our [libpostal(Windows) installation guide](./setup/libpostal_windows.md) for help with installing on windows.
  - It's already installed on the Docker instance, if you'd like to run/debug there.

## In use:

```python
from sgpostal.sgpostal import parse_address_usa, parse_address_intl, SgAddress

an_address_in_the_usa    = parse_address_usa('836 Prudential Drive, Jacksonville, Florida 12345')
an_international_address = parse_address_intl('221B Baker Street, London, NW1 6XE, UK')
```

## Return type

```python
@dataclass(frozen=True)
class SgAddress:
    """
    Canonical representation of address.
    """
    country: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    street_address_1: Optional[str] = None
    street_address_2: Optional[str] = None
```

## Nuances, fall-backs, and other considerations (MUST READ)

- Oftentimes, the raw address cannot be parsed. This can be due to many reasons - either because it's in a format that
  the library can't parse, there's some data missing, or there is high ambiguity.
- This means that one or more of the fields in the resulting `SgAddress` will be `None`. You should check for that, and discuss with QA / business if it's acceptable.
- You should always populate the `SgRecord(raw_address=...)` field with the raw address field, if you're using `sgpostal`. 
