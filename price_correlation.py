import pandas as pd
import matplotlib.pyplot as plt
from pyzipcode import ZipCodeDatabase
from scipy.stats import pearsonr

zcdb = ZipCodeDatabase()


def ziplat(x):
    '''Takes in a five digit zipcode and returns latitude
    ''' 
    try:
        return round(zcdb[x].latitude,2)
    except:
        pass
 
def ziplon(x):
    '''Takes in a five digit zipcode and returns longitude
    '''   
    try:
        return round(zcdb[x].longitude,2)
    except:
        pass

def zipcity(x):
    '''Takes in a five digit zipcode and returns a city
    '''
    try:
       return zcdb[x].city
    except:
       pass
    
def demean(x):
    '''Function used to normalize(demean) prices
    '''
    return x/x.mean()

def pearson_corr(x):
    '''Takes in the name of a bundle and calculates the pearson coefficient
    '''
    mask = bundle['bundle'] == x
    bundle[mask]
    return pearsonr(bundle[mask]['income'], bundle[mask]['price'])[0]


def p_value(x):
    '''Takes in the name of a bundle and calculates the p_value 
       of the pearson coefficient
    '''
    mask = bundle['bundle'] == x
    bundle[mask]
    return pearsonr(bundle[mask]['income'], bundle[mask]['price'])[1]


def plotting_by_bundle(x):
    '''Plots a bar plot of income and prices per bundle
       and per zipcode
    '''
    mask = bundle['bundle'] == 'vegetables'
    plt_df = pd.DataFrame(bundle[mask], columns=['income', 'price'])
    plt_df.plot(kind='bar')



# Loading csv files

incomezip = pd.read_csv("/home/ubuntu/Documents/us-income-by-zip-12zpallagi.csv") 
sdobserv = pd.read_csv("/home/ubuntu/Documents/premise-us-sandiego-observations.csv")
foodtax = pd.read_csv("/home/ubuntu/Documents/premise-us-food-taxonomy.csv")
zipcsv = pd.read_csv("/home/ubuntu/Documents/latlondict.csv")                #Helper file that will help map latitudes and longitudes to zipcodes



# Filtering for state of CA zipcodes and creating a new dataframe: income_df

mask = incomezip['STATE'] == 'CA'
cazip = incomezip[mask]

income_df = pd.DataFrame({'STATE': cazip['STATE'], 'zipcode': cazip['zipcode'], 
                          'N1':cazip['N1'], 'A00100':cazip['A00100']})




# Calculating average adjusted gross income by zip code

income_df = income_df[income_df.zipcode != 0]  
income_df = income_df[income_df.zipcode != 99999]
 
income_df['N*A00100'] = income_df['A00100']*income_df['N1']

group1 = income_df.groupby('zipcode')['N*A00100']
group2 = income_df.groupby('zipcode')['N1']
income_df['weight_avg'] = group1.transform(sum)/group2.transform(sum)

income_df['AAGI'] = income_df['weight_avg']/group2.transform(len)




# Adding latitude ('lat'), longitude('lon') and city to income_df dataframe 

income_df['lat'] = income_df['zipcode'].apply(lambda x: ziplat(x))
income_df['lon'] = income_df['zipcode'].apply(lambda x: ziplon(x))
income_df['city'] = income_df['zipcode'].apply(lambda x : zipcity(x))


# Creating new abbreviated data frames foodtax_df for food taxonomy and sdobs_df for San Diego observations

foodtax_df = pd.DataFrame({'uuid': foodtax['uuid'],'bundle':foodtax['bundle']})

sdobs_df = pd.DataFrame({'lat':sdobserv['loc_lat'],'lon':sdobserv['loc_long'],
                         'norm_pr':sdobserv['normalized_price'],'norm_su':sdobserv['normalized_size_units'],
                         'spec_uuid':sdobserv['spec_uuid'],'spec_prod':sdobserv['spec_product']})





   
s_uuid = sdobs_df['spec_uuid'].apply(lambda x : x)                           # Extraction of uuid's from sdobs_df
food_dict = foodtax_df.set_index('uuid')['bundle'].to_dict()                 # Creation of a taxonomy dictionary from foodtax_df
sdobs_df['bundle']=s_uuid.apply(lambda x : food_dict[x])                     # Adding column 'bundle' to sdobs_df using the food dictionary

sdobs_df['lat'] = sdobs_df['lat'].apply(lambda x : round(x,2))               
sdobs_df['lon'] = sdobs_df['lon'].apply(lambda x : round(x,2))

group = sdobs_df.groupby(['spec_uuid','norm_su'])                            # Price demean by grouping by product and 
sdobs_df['demean_pr'] = group['norm_pr'].transform(demean)                   # normalized size units  



 
s_lat = sdobs_df['lat'].apply(lambda x : x)                                 # Adding 'latlon' and 'zipcode' columns to help 
s_lon = sdobs_df['lon'].apply(lambda x : x)                                 # with populating 'zipcode ' with zipcodes.
s_latlon = pd.Series(zip(s_lat,s_lon))
sdobs_df['latlon'] = s_latlon
sdobs_df['zipcode'] = ""

zip_lat = zipcsv['lat'].apply(lambda x : x)                                  # Dictionary created from extra csv file.
zip_lon = zipcsv['lon'].apply(lambda x : x)     
zip_latlon = pd.Series(zip(zip_lat,zip_lon))
zipcsv['latlon'] = zip_latlon
zip_dict = zipcsv.set_index('latlon')['zipcode'].to_dict()


# Populating sdobs_df 'zipcode' column with zipcodes  

for i in range(len(sdobs_df['latlon'])):     
    try:
       sdobs_df.zipcode[i] = zip_dict[sdobs_df.latlon[i]]
    except:
       sdobs_df.zipcode[i] = 92111                                          # 92111 is being used as a default zipcode



# Merging sdobs_df and income_df on 'zipcode' column using a left join

merged_df = pd.merge(sdobs_df,income_df, on='zipcode', how ='left')
group = merged_df.groupby(['bundle','zipcode','AAGI'])                       # Grouping by 'bundle','zipcode','AAGI'.
bundle_zip_pr = group['demean_pr'].apply(lambda x : x.mean())                # Calculating demeaned price by bundle, zipcode.      




bundle_zip_pr = pd.Series(bundle_zip_pr)                                     
bundle_zip_pr.to_csv("bundle_zip_price.csv")                                 # Saving prices to a csv in order to extract later as 
bundle = pd.read_csv("/home/ubuntu/Documents/bundle_zip_price.csv")          # a dataframe. Note saves to /home must be moved.
bundle.columns = ['bundle','zipcode','income', 'price']                      # Attaching names to columns.


zips = list(set(bundle['zipcode']))
products = list(set(bundle['bundle']))

corr_df = pd.DataFrame()                                                     # Creating a new dataframe for correlation coefficients.
corr_df['bundle']=products                                                   # Adding column with products and empty columns for correlation
corr_df['correlation']=''                                                    # and p_value. 
corr_df['p_val']=''


corr_df['correlation'] = corr_df['bundle'].apply(lambda x : pearson_corr(x))
corr_df['p_val'] = corr_df['bundle'].apply(lambda x : p_value(x))
corr_df
corr_df.to_csv("corr_df.csv")                                                # Saving correlation dataframe to a csv file.




plotting_by_bundle('vegetables')                                             # Example of using plotting function with vegtable bundle.




















