const MISSING = '<MISSING>';

class Poi {
  constructor({
    locator_domain = MISSING,
    location_name = MISSING,
    street_address = MISSING,
    city = MISSING,
    state = MISSING,
    zip = MISSING,
    country_code = MISSING,
    store_number = MISSING,
    phone = MISSING,
    location_type = MISSING,
    latitude = MISSING,
    longitude = MISSING,
    hours_of_operation = MISSING,
  }) {
    /* eslint-disable camelcase */
    this.locator_domain = locator_domain;
    this.location_name = location_name;
    this.street_address = street_address;
    this.city = city;
    this.state = state;
    this.zip = zip;
    this.country_code = country_code;
    this.store_number = store_number;
    this.phone = phone;
    this.location_type = location_type;
    this.latitude = latitude;
    this.longitude = longitude;
    this.hours_of_operation = hours_of_operation;
  }
}

module.exports = {
  Poi,
};
