const noDataLabel = '<MISSING>';

class Poi {
  constructor({
    locator_domain = noDataLabel,
    location_name = noDataLabel,
    street_address = noDataLabel,
    city = noDataLabel,
    state = noDataLabel,
    zip = noDataLabel,
    country_code = noDataLabel,
    store_number = noDataLabel,
    phone = noDataLabel,
    location_type = noDataLabel,
    latitude = noDataLabel,
    longitude = noDataLabel,
    hours_of_operation = noDataLabel,
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
