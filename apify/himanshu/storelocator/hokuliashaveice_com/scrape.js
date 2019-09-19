const Apify = require('apify');
const request=require('request');
const cheerio=require('cheerio');

var url = 'https://hokuliashaveice.com/locations/';

 
 
async function scrape(){
  return new Promise(async (resolve,reject)=>{
request(url,(err,res,html)=>{
                    if(!err && res.statusCode==200){
                      
                          const $  =cheerio.load(html);
                           
                          var items=[];

                           var main = $('.mod-locations').find('.col-xs-6');
                           function mainhead(i)

                             {
                                 if(main.length>i)
   
                                     {
                             var address_tmp = $('.mod-locations').find('.col-xs-6').eq(i).html().split('<br>');
                             
                             if(address_tmp.length == 2){
                              var location_name = '';
                              var address =  '';
                              var city =  '';
                              var state =  '<MISSING>';
                              var zip =  '<MISSING>';
                              var latitude =  '<MISSING>';
                              var longitude =  '<MISSING>';
                             }
                             else if(address_tmp.length == 3){
                              var location_name = address_tmp[0].trim().replace('700 US-29 N.','<MISSING>');
                              var address_tmp1 = address_tmp[1].trim().split('<');
                              var address_tmp2 = address_tmp1[0].split(',');
                            
                                    if(address_tmp2.length ==2){
                                      var address = address_tmp2[0].replace('Athens','<MISSING>');
                                      var city_tmp = address_tmp2[1].trim().split(' ');
                                       
                                      if(city_tmp.length == 1){
                                        var city = address_tmp2[0];
                                        var state = city_tmp[0];
                                        var zip = '<MISSING>';

                                      }
                                      else if(city_tmp.length ==3){
                                        var city = city_tmp[0];
                                        var state = city_tmp[1];
                                        var zip = city_tmp[2];
                                      }
                                     

                                    }
                                   else if(address_tmp2.length ==3){
                                     
                                      var address = address_tmp2[0];
                                      var city = address_tmp2[1];
                                      var state_tmp = address_tmp2[2].trim().split(' ');
                                      var state = state_tmp[0];
                                      var zip = state_tmp[1];
                                      
                                      
                                    }
                                   else if(address_tmp2.length ==4){
                                      
                                    var address = address_tmp2[0]+''+address_tmp2[1];
                                    var city = address_tmp2[2];
                                    var state_tmp = address_tmp2[3].trim().split(' ');
                                    var state = state_tmp[0];
                                    var zip = state_tmp[1];
                                     
                                    }

                                    var latitude_tmp =$('.mod-locations').find('.col-xs-6').eq(i).find('a').attr('href');
                                    if(typeof latitude_tmp!='undefined'){
                                      var latitude_tmp1 = latitude_tmp.split('/@');
                                      var latitude_tmp2 = latitude_tmp1[1].split(',');
                                      var latitude = latitude_tmp2[0];
                                      var longitude = latitude_tmp2[1];
                                     
                                    }
                                    else {
                                      var latitude = '<MISSING>';
                                      var longitude = '<MISSING>';
                                    }
                                    
                             
                            

                             }
                             else if(address_tmp.length == 4){
                               var location_name = address_tmp[0].trim();
                               var address = address_tmp[1].trim().replace('Athens, GA','1143 Prince Ave');
                               var city_tmp = address_tmp[2].trim().split('<');
                               var city_tmp1 = city_tmp[0].replace('(Piedmont Athens Regional Hospital)','Athens, GA').trim().split(',');
                               var city = city_tmp1[0];
                               var state_tmp = city_tmp1[1].split(' ');
                               
                               if(state_tmp.length ==2){
                                 var state = state_tmp[1];
                                 var zip = '<MISSING>';

                               }
                              else if(state_tmp.length ==3){
                                 var state = state_tmp[1];
                                 var zip = state_tmp[2];
                                 
                              }
                              else if(state_tmp.length ==4){
                                var state = state_tmp[1];
                                 var zip = state_tmp[3];
                                 
                              }
                              
                              
                               var latitude_tmp =$('.mod-locations').find('.col-xs-6').eq(i).find('a').attr('href');
                               if(typeof latitude_tmp!='undefined'){
                                var latitude_tmp =$('.mod-locations').find('.col-xs-6').eq(i).find('a').attr('href');
                                
                                var latitude_tmp1 = latitude_tmp.split('/@');
                                        if(latitude_tmp1.length == 2){
                                          var latitude_tmp2 = latitude_tmp1[1].split(',');
                                          var latitude = latitude_tmp2[0];
                                          var longitude = latitude_tmp2[1];
                                        

                                        }
                                        else if(latitude_tmp1.length == 3){
                                          var latitude_tmp2 = latitude_tmp1[1].split(',');
                                          var latitude = latitude_tmp2[0];
                                          var longitude = latitude_tmp2[1];
                                          
                                        }
                                        else if(latitude_tmp1.length == 1){
                                          var latitude = '<MISSING>';
                                          var longitude = '<MISSING>';
                                          
                                        }
                                 
                                
                               
                              }
                              else {
                                var latitude = '<MISSING>';
                                var longitude = '<MISSING>';
                              } 
                               
                                
                               
                             }
                             else if (address_tmp.length ==5){
                              var location_name = address_tmp[0].trim();
                              var address = address_tmp[1].trim().replace('Next to Burberry/Blaze Pizza','48400 Seminole Dr').replace('(Near Honeybaked Ham)','1083 W Riverdale Rd').replace('Shadow Point Shopping Center','1235 W 1700 S');
                              var city_tmp = address_tmp[3].trim().split('<a');
                              var city_tmp1 = city_tmp[0];
                              if(city_tmp1!=''){
                                var city_tmp1 = city_tmp[0].trim().split(',');
                                var city = city_tmp1[0];
                                var state_tmp = city_tmp1[1].split(' ');
                                if(state_tmp.length == 3){
                                  var state = state_tmp[1];
                                  var zip = state_tmp[2];

                                }
                                if(state_tmp.length == 2){
                                  var state = state_tmp[1];
                                  var zip = '<MISSING>';

                                }
                                
                              

                              }
                              else{
                                var city_tmp = address_tmp[2].trim().split(',');
                                var city = city_tmp[0];
                                var state_tmp = city_tmp[1].split(' ');
                                 if(state_tmp.length == 3){
                                   var state = state_tmp[1];
                                   var zip = state_tmp[2];

                                 }
                                 else if (state_tmp.length ==2){
                                   var state = state_tmp[1];
                                   var zip = '<MISSING>';

                                 }
                                
                              }
                              var latitude_tmp =$('.mod-locations').find('.col-xs-6').eq(i).find('a').attr('href');
                              var latitude_tmp1 = latitude_tmp.split('/@');
                              var latitude_tmp2 = latitude_tmp1[1].split(',');
                              var latitude = latitude_tmp2[0];
                              var longitude = latitude_tmp2[1];
                             
                             
                                 
                             }
                             else if(address_tmp.length ==6){
                              var location_name = address_tmp[0].trim();
                              var address = address_tmp[2].replace('Olathe, KS 66061','11118 S. Lone Elm Rd #104');
                              var city_tmp = address_tmp[3].trim().replace('(913)289-5400','Olathe, KS 66061').split(',');
                              var city = city_tmp[0];
                              var state_tmp = city_tmp[1].split(' ');
                              var state= state_tmp[1];
                              var zip = state_tmp[2];
                              var latitude_tmp =$('.mod-locations').find('.col-xs-6').eq(i).find('a').attr('href');
                              var latitude_tmp1 = latitude_tmp.split('/@');
                              var latitude_tmp2 = latitude_tmp1[1].split(',');
                              var latitude = latitude_tmp2[0];
                              var longitude = latitude_tmp2[1];
                              

                             }
                             else if(address_tmp.length ==7){
                              var location_name = '<MISSING>';
                              var address = address_tmp[0].trim();
                              var city_tmp = address_tmp[2].trim().split(' ');
                              var city = city_tmp[0].replace(',','');
                              var state = city_tmp[1].replace('.','');
                              var zip = city_tmp[2];
                               

                             }
                           
                               if(location_name!=''){
                                items.push({  

                                  locator_domain: 'https://hokuliashaveice.com/', 
  
                                  location_name: location_name, 
                      
                                  street_address: address,
                      
                                  city: city, 
                      
                                  state: state,
                      
                                  zip:  zip,
                      
                                  country_code: 'US',
                      
                                  store_number: '<MISSING>',
                      
                                  phone: '<MISSING>',
                      
                                  location_type: 'hokuliashaveice',
                      
                                  latitude: latitude,
                      
                                  longitude: longitude, 
                      
                                  hours_of_operation: '<MISSING>'});

                               }
                               
                            
                                       
                            mainhead(i+1);
                              
                          }
                                
                                
                          else{
                      
                          resolve(items);
                      
                          }
                    } 
  
                    mainhead(1);   
  }
 
 });
})
}
  
Apify.main(async () => {

    

    const data = await scrape();
   
   await Apify.pushData(data);
    
  
  });
