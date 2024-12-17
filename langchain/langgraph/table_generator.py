import pandas as pd

# Creating a dictionary with the GDP data of the United States from 2000 to 2020
us_gdp_data = {
    'Year': list(range(2000, 2021)),
    'GDP (in trillion USD)': [10.25, 10.58, 10.93, 11.51, 12.27, 13.09, 13.86, 14.48, 14.72, 14.45, 14.96, 15.52, 16.16, 16.66, 17.43, 18.12, 18.71, 19.39, 20.58, 21.43, 21.00]  # 2020 is an estimate
}

# Creating a DataFrame from the dictionary
gdp_df = pd.DataFrame(us_gdp_data)
print(gdp_df)
