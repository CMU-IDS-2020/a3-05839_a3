import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

POPU_DIST = "Population Distribution by Country"
OVERVIEW = 'Overview'
SINGLE_FACTOR_OVER_TIME = 'What affects life expectancy?'
# locations of data
HEALTH_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/health.csv"
MERGED_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/merged_data_country_only.csv"

def main():


	# Add a selector for the app mode on the sidebar.
	st.sidebar.title("Navigation")
	vis_topic = st.sidebar.radio("",
		(str(OVERVIEW), str(POPU_DIST), str(SINGLE_FACTOR_OVER_TIME)))
	if vis_topic == OVERVIEW:
		# Render main readme, placeholder
		readme_text = st.markdown("readme.md")
	elif vis_topic == POPU_DIST:
		st.title(POPU_DIST)
		run_popu_dist()
	elif vis_topic == SINGLE_FACTOR_OVER_TIME:
		st.title(SINGLE_FACTOR_OVER_TIME)
		run_trend_over_time()

@st.cache
def load_data(url):
    data = pd.read_csv(url, header=0, skipinitialspace=True)
    countries = data['Country Name'].unique()
    return data, countries

@st.cache
def group_by_country(df):    
	return df.groupby(['Country Name'])

@st.cache
def load_health_data():
	df, countries = load_data(HEALTH_URL)
	return df, countries

@st.cache
def load_merge_data():
	df, countries = load_data(MERGED_URL)
	df['Year'] = pd.to_datetime(df['Year'], format='%Y')
	return df, countries


@st.cache
def data_group_by_country(df):
	grouped = dict(tuple(group_by_country(df)))
	return grouped	

@st.cache
def keep_only_selected_countries(df, selected_countries):
	sub_df = df[df['Country Name'].isin(selected_countries)]
	return sub_df

def run_popu_dist():

	@st.cache
	def get_total_ymax(country_df, health_df):
		# fixing y range for better visualizing the change
		maxy = 0.0
		for col in country_df.columns:
		    if '% of' in col and 'Population ages' in col:
		        curr_max = health_df[col].max()
		        if curr_max > maxy:
		            maxy = curr_max	
		return maxy            

	# load health data
	health_df, countries = load_health_data()
	health_grouped = data_group_by_country(health_df)

	st.sidebar.header("Adjust Parameters")

	country = st.sidebar.selectbox("Country", countries)
	country_df = health_grouped[country]

	by_gender = st.sidebar.checkbox('View By Gender', value=False)

	max_year = country_df['Year'].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(country_df['Year'].unique())), value=max_year)

	# # plot based on the country, hack for not displaying the column index
	# st.dataframe(country_df.assign(hack='').set_index('hack'))

	# plot the histogram base on country and year
	row = country_df.loc[country_df['Year'] == year]

	if by_gender:
		age_ranges = ['15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 and above']
		male_values = []
		female_values = []
		for r in age_ranges:
			male_values.append(row['Population ages {}, male (% of male population)'.format(r)].item())
			female_values.append(row['Population ages {}, female (% of female population)'.format(r)].item())
		
		curr_data = pd.DataFrame({'Population ages': age_ranges, '% of Male Population': male_values, '% of Female Population': female_values})
		maxx = curr_data['% of Male Population'].max()
		if curr_data['% of Female Population'].max().item() > maxx:
			maxx = curr_data['% of Female Population'].max()

		base = alt.Chart(curr_data).properties(width=300)
		# highlight selector
		highlight = alt.selection_single(on='mouseover', fields=['Population ages'], nearest=False, clear="mouseout")

		left = base.encode(
		    y=alt.Y('Population ages', axis=None),
		    x=alt.X('% of Female Population',
		            title='% of Female Population',
		            sort=alt.SortOrder('descending'),
		            scale=alt.Scale(domain=(0, maxx))),
		    color=alt.condition(
		        ~highlight,
		        alt.Color('Population ages:O', scale=alt.Scale(scheme='redpurple'), legend=None),
		        alt.value('orange'),     # which sets the bar orange.
		    ),
		    tooltip=['Population ages', '% of Female Population']
		).mark_bar().properties(title='Female').interactive().add_selection(highlight)

		middle = base.encode(
		    y=alt.Y('Population ages', axis=None),
		    text=alt.Text('Population ages'),
		).mark_text().properties(width=40)

		right = base.encode(
		    y=alt.Y('Population ages', axis=None),
		    x=alt.X('% of Male Population',
		            title='% of Male Population',
		            sort=alt.SortOrder('ascending'),
		            scale=alt.Scale(domain=(0, maxx))),
		    color=alt.condition(
		        ~highlight,
		        alt.Color('Population ages:O',scale=alt.Scale(scheme='blues'), legend=None),
		        alt.value('orange'),     # which sets the bar orange.
		    ),
		    tooltip=['Population ages', '% of Male Population']
		).mark_bar().properties(title='Male').interactive().add_selection(highlight)

		bihist=alt.concat(left, middle, right, spacing=2).resolve_scale(color='independent')
		st.altair_chart(bihist, use_container_width=True)

	else:
		age_ranges = ['0-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 and above']
		values = []
		for r in age_ranges:
			values.append(row['Population ages {} (% of total population)'.format(r)].item())
		curr_data = pd.DataFrame({'Population ages': age_ranges, '% of Total Population': values})

		# highlight selector
		highlight = alt.selection_single(on='mouseover', fields=['Population ages'], nearest=False, clear="mouseout")

		hist = alt.Chart(curr_data).mark_bar().encode(
		    alt.X('% of Total Population',
		    	scale=alt.Scale(domain=(0, get_total_ymax(country_df, health_df)))),
		    y='Population ages',
		    color=alt.condition(
		        ~highlight,
		        alt.Color('Population ages:O', scale=alt.Scale(scheme='greens'), legend=None),
		        alt.value('orange'),     # which sets the bar orange.
		    ),
		    tooltip=['Population ages', '% of Total Population']
		).interactive().add_selection(highlight)
		st.altair_chart(hist, use_container_width=True)

def run_trend_over_time():

	data, countries = load_merge_data()

	# always plot the life expectancy
	life_exp = alt.Chart(data).mark_line().encode(
		x=alt.X('Year:T', axis = alt.Axis(title = 'Year', format = ("%Y"))),
	    y='Life expectancy at birth, total (years)',
	    color='Country Name'
	)

	# drop box to select one variable to view
	st.sidebar.header("Adjust Parameters")

	factors = ['Gini',
       'Current health expenditure (% of GDP)',
       'Current health expenditure per capita (current US$)',
       'GDP per capita (current US$)',
       'Unemployment, total (% of total labor force)']

	factor = st.sidebar.selectbox("Additional Factors", factors)

	selected_countries = st.sidebar.multiselect('Select Countries to compare', countries)
	# plot factor countries over time
	if selected_countries:

		curr_df = keep_only_selected_countries(data, selected_countries)
		factor_plot = alt.Chart(curr_df).mark_line().encode(
		    x=alt.X('Year:T', axis = alt.Axis(title = 'Year', format = ("%Y"))),
		    y=str(factor),
		    color='Country Name'
		)
		st.altair_chart(factor_plot, use_container_width=True)
		life_exp_sub = alt.Chart(curr_df).mark_line().encode(
		    x=alt.X('Year:T', axis = alt.Axis(title = 'Year', format = ("%Y"))),
		    y='Life expectancy at birth, total (years)',
		    color='Country Name'
		)
		st.altair_chart(life_exp_sub, use_container_width=True)
	else:
		st.altair_chart(life_exp, use_container_width=True)

if __name__ == "__main__":
    main()