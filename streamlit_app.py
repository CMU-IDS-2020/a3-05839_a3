import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

POPU_DIST = "Population Distribution"
OVERVIEW = 'Overview'
# locations of data
HEALTH_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/health.csv"

def main():


	# Add a selector for the app mode on the sidebar.
	st.sidebar.title("Navigation")
	vis_topic = st.sidebar.radio("",
		(str(OVERVIEW), str(POPU_DIST), ))
	if vis_topic == OVERVIEW:
		# Render main readme, placeholder
		readme_text = st.markdown("readme.md")
	if vis_topic == POPU_DIST:
		st.write(POPU_DIST)
		run_popu_dist()

@st.cache
# load and pre-process data
def load_data(url):
    data = pd.read_csv(url, header=0, skipinitialspace=True)
    return data

@st.cache
def group_by_country(df):    
	return df.groupby(['Country Name'])

@st.cache
def load_health_data():
	df = load_data(HEALTH_URL)
	coutries = df['Country Name'].unique()
	return df, coutries


def run_popu_dist():

	@st.cache
	def health_group_by_country(df):
		grouped = dict(tuple(group_by_country(df)))
		return grouped

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
	health_grouped = health_group_by_country(health_df)

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

		left = base.encode(
		    y=alt.Y('Population ages', axis=None),
		    x=alt.X('% of Female Population',
		            title='% of Female Population',
		            sort=alt.SortOrder('descending'),
		            scale=alt.Scale(domain=(0, maxx))),
		    color=alt.Color('Population ages:O', scale=alt.Scale(scheme='redpurple'), legend=None),
		    tooltip=['Population ages', '% of Female Population']
		).mark_bar().properties(title='Female').interactive()

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
		    color=alt.Color('Population ages:O',scale=alt.Scale(scheme='blues'), legend=None),
		    tooltip=['Population ages', '% of Male Population']
		).mark_bar().properties(title='Male').interactive()

		bihist=alt.concat(left, middle, right, spacing=2).resolve_scale(color='independent')
		st.altair_chart(bihist, use_container_width=True)

	else:
		age_ranges = ['0-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 and above']
		values = []
		for r in age_ranges:
			values.append(row['Population ages {} (% of total population)'.format(r)].item())
		curr_data = pd.DataFrame({'Population ages': age_ranges, '% of Total Population': values})

		hist = alt.Chart(curr_data).mark_bar().encode(
		    alt.X('% of Total Population',
		    	scale=alt.Scale(domain=(0, get_total_ymax(country_df, health_df)))),
		    y='Population ages',
		    color=alt.Color('Population ages:O', scale=alt.Scale(scheme='greens'), legend=None),
		    tooltip=['Population ages', '% of Total Population']
		).interactive()
		st.altair_chart(hist, use_container_width=True)

if __name__ == "__main__":
    main()