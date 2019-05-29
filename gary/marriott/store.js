const createCsvWriter = require('csv-writer').createArrayCsvWriter;

const NO_DATA = 'NO-DATA';

class Store {
  constructor(locator_domain,
              locator_name,
              street_address,
              city,
              state,
              zip,
              country_code,
              store_number,
              phone,
              location_type,
              naics_code,
              latitude,
              longitude,
              external_lat_lon,
              hours_of_operation) {
    this.locator_domain = locator_domain;
    this.locator_name = locator_name;
    this.street_address = street_address.trim();
    this.city = city.trim();
    if (state.trim().length == 0) {
      this.state = NO_DATA;
    } else {
      this.state = state;
    }
    this.state = state.trim();
    this.zip = zip.trim();
    this.country_code = country_code.trim();
    this.store_number = store_number;
    
    if (phone == null) {
      this.phone = NO_DATA;
    } else {
      let phone_ = phone.split('-').join('');
      if (phone_.match(/^\d{10}$/) != null) {
        this.phone = phone_;
      } else if(phone == NO_DATA) {
        this.phone = phone;
      } else if(phone.startsWith('+1 ')) {
        this.phone = phone_.split('+1 ')[1];
      } else {
        this.phone = NO_DATA;
      }
    }
    
    this.location_type = location_type;
    this.naics_code = naics_code;
    this.latitude = latitude.trim();
    this.longitude = longitude.trim();
    this.external_lat_lon = external_lat_lon;
    this.hours_of_operation = hours_of_operation.trim();
  }

  toString() {
    return `${this.locator_domain},${this.locator_name},${this.street_address},${this.city},${this.state},${this.zip},${this.country_code},${this.store_number},${this.phone},${this.location_type},${this.naics_code},${this.latitude},${this.longitude},${this.external_lat_lon},${this.hours_of_operation}`
  }

  toArray() {
    return [this.locator_domain, this.locator_name, this.street_address, this.city, this.state, this.zip, this.country_code, this.store_number, this.phone, this.location_type, this.naics_code, this.latitude, this.longitude, this.external_lat_lon, this.hours_of_operation];
  }
}

class Stores {
  constructor(outputToCSV, csvFile) {
    this.outputToCSV = outputToCSV;
    this.csvFile = csvFile;
    this.stores = [];
    this.header = 'locator_domain,location_name,street_address,city,state,zip,country_code,store_number,phone,location_type,naics_code,latitude,longitude,hours_of_operation';
  }

  addStore(store) {
    this.stores.push(store);
  }

  async write() {
    if (this.outputToCSV) {
      console.log(this.csvFile);
      const csvWriter = createCsvWriter({
        header: this.header.split(','),
        path: this.csvFile
      });
      const rows = this.stores.map(store => store.toArray());
      csvWriter.writeRecords(rows)
    } else {
      console.log(this.header);
      for (let store of this.stores) {
        console.log(store.toString());
      }
    }
  }
}

module.exports.Store   = Store;
module.exports.Stores  = Stores;
module.exports.NO_DATA = NO_DATA
