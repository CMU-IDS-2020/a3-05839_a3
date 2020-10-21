import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from vega_datasets import data


OVERVIEW = "Overview"
POPU_DIST = "Population Distribution"
VAR_RELATIONSHIP_PER_COUNTRY = "Health & Economy Interaction, per Country"
ONE_VAR_ACROSS_REGION = "Health / Economy over the World"
# locations of data
HEALTH_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/health.csv"
OTHER_DATA_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/merged_data_country_only_with_id_lat_lon.csv"


def main():
	# Add a selector for the app mode on the sidebar.
	st.sidebar.title("Navigation")
	vis_topic = st.sidebar.radio("",
		(str(OVERVIEW), str(POPU_DIST), str(VAR_RELATIONSHIP_PER_COUNTRY), str(ONE_VAR_ACROSS_REGION)))
	if vis_topic == OVERVIEW:
		# Render main readme, placeholder
		readme_text = st.markdown("readme.md")
	if vis_topic == POPU_DIST:
		st.write(POPU_DIST)
		run_popu_dist()
	if vis_topic == VAR_RELATIONSHIP_PER_COUNTRY:
		st.write(VAR_RELATIONSHIP_PER_COUNTRY)
		run_var_relationship_per_country()
	if vis_topic == ONE_VAR_ACROSS_REGION:
		st.write(ONE_VAR_ACROSS_REGION)
		run_one_var_across_region()


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

@st.cache
def load_other_data():
	df = load_data(OTHER_DATA_URL)
	df['id'] = df['id'].astype(str)
	df['id'] = df['id'].str.zfill(3)
	countries = df['Country Name'].unique()
	econ_indicators = df.columns[[3, 6, 8]]
	health_indicators = df.columns[[4, 5, 7]]
	return df, countries, econ_indicators, health_indicators


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


def run_var_relationship_per_country():
	other_data_df, countries, econ_indicators, health_indicators = load_other_data()

	st.sidebar.header("Adjust Parameters")

	country = st.sidebar.selectbox("Country", countries)
	country_df = other_data_df[other_data_df["Country Name"] == country]

	econ_indicator = st.sidebar.selectbox("Economy Indicator", econ_indicators)
	health_indicator = st.sidebar.selectbox("Health Indicator", health_indicators)
	bi_var_df = country_df[["Year", econ_indicator, health_indicator]]

	if bi_var_df.dropna().empty:
		st.write("Data Not Available")
	else:
		base = alt.Chart(bi_var_df).encode(
			alt.X('Year', axis=alt.Axis(title=None))
		)
		line1 = base.mark_line(color='#5276A7').encode(
			alt.Y(econ_indicator,
				  axis=alt.Axis(title=econ_indicator, titleColor='#5276A7'))
		)
		line2 = base.mark_line(color='#57A44C').encode(
			alt.Y(health_indicator,
				  axis=alt.Axis(title=health_indicator, titleColor='#57A44C'))
		)
		line_plot = alt.layer(line1, line2).resolve_scale(
			y='independent'
		)
		st.altair_chart(line_plot, use_container_width=True)


def run_one_var_across_region():
	countries = alt.topo_feature(data.world_110m.url, 'countries')
	other_data_df, _, econ_indicators, health_indicators = load_other_data()
	st.sidebar.header("Adjust Parameters")

	indicator = st.sidebar.selectbox("Health / Economy Indicator", list(econ_indicators) + list(health_indicators))
	uni_var_df = other_data_df[["Country Name", "Year", indicator, 'id', 'Latitude (average)', 'Longitude (average)']]

	max_year = uni_var_df["Year"].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(uni_var_df['Year'].unique())), value=max_year)
	uni_var_one_year_df = uni_var_df[uni_var_df["Year"] == year]

	if uni_var_one_year_df.dropna().empty:
		st.write("Data Not Available")
	else:
		map = alt.Chart(countries).mark_geoshape().encode(
			color=alt.Color(indicator+':Q', scale=alt.Scale(scheme="plasma"))
		).transform_lookup(
			lookup='id',
			from_=alt.LookupData(uni_var_one_year_df, 'id', [indicator])
		).project(
			'equirectangular'
		)
		hover = alt.selection(type='single', on='mouseover', nearest=True,
							  fields=['Longitude (average)', 'Latitude (average):Q'])
		points = alt.Chart(uni_var_one_year_df).mark_circle(
			point = 'transparent'
		).encode(
			longitude='Longitude (average):Q',
			latitude='Latitude (average):Q',
			opacity=alt.value(0),
			tooltip=['Country Name:N', indicator+':Q']
		).add_selection(hover)
		map = map + points
		st.altair_chart(map, use_container_width=True)

if __name__ == "__main__":
    main()