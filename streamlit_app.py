import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

POPU_DIST = "Population Distribution by Country"
OVERVIEW = 'Overview'
SINGLE_FACTOR_OVER_TIME = 'What affects life expectancy?'
POINT2_PLACEHOLDER = 'Point2 Graph'
# locations of data
HEALTH_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/health.csv"
MERGED_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/merged_data_country_only.csv"

def main():


	# Add a selector for the app mode on the sidebar.
	st.sidebar.title("Navigation")
	vis_topic = st.sidebar.radio("",
		(str(OVERVIEW), str(POPU_DIST), str(SINGLE_FACTOR_OVER_TIME), str(POINT2_PLACEHOLDER)))
	if vis_topic == OVERVIEW:
		# Render main readme, placeholder
		readme_text = st.markdown("readme.md")
	elif vis_topic == POPU_DIST:
		st.title(POPU_DIST)
		run_popu_dist()
	elif vis_topic == SINGLE_FACTOR_OVER_TIME:
		st.title(SINGLE_FACTOR_OVER_TIME)
		run_trend_over_time()
	elif vis_topic == POINT2_PLACEHOLDER:
		st.title(POINT2_PLACEHOLDER)
		run_relationship_per_year_all_countries()

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

	data_cached, countries = load_merge_data()
	data = data_cached.copy()
	data['Year'] = pd.to_datetime(data['Year'], format='%Y')

	# always plot the life expectancy
	life_exp = alt.Chart(data).mark_line().encode(
		x=alt.X('Year:T', axis = alt.Axis(title = 'Year', format = ("%Y"))),
	    y='Life expectancy at birth, total (years)',
	    color='Country Name'
	)

	# drop box to select one variable to view
	st.sidebar.header("Adjust Parameters")

	factors = [
       'Current health expenditure (% of GDP)',
       'Current health expenditure per capita (current US$)',
       'GDP per capita (current US$)',
       'Unemployment, total (% of total labor force)'
       'Gini',]

	factor = st.sidebar.selectbox("Additional Factors", factors)

	selected_countries = st.sidebar.multiselect('Select Countries to compare', countries)

	# plot factor countries over time
	if selected_countries:

		curr_df = keep_only_selected_countries(data, selected_countries)

		line_p = alt.Chart(curr_df).mark_line().encode(
		    x=alt.X('Year:T', axis = alt.Axis(title = 'Year', format = ("%Y"))),
		    color='Country Name'
		)
		upper = line_p.encode(y=str(factor))
		lower = line_p.encode(y='Life expectancy at birth, total (years)')

		# Create a selection that chooses the nearest point & selects based on x-value
		nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        		fields=['Year'], empty='none')
		idx = 0
		plots = [upper, lower]
		result_plots = []
		for line in plots:

			# Transparent selectors across the chart. This is what tells us
			# the x-value of the cursor
			selectors = alt.Chart(curr_df).mark_point().encode(
			    x='Year',
			    opacity=alt.value(0),
			)
			if idx == 0:
				selectors = selectors.add_selection(nearest)

			# Draw a rule at the location of the selection
			rules = alt.Chart(curr_df).mark_rule(color='darkgray').encode(
			    x='Year',
			).transform_filter(
			    nearest
			)
			# Draw points on the line, and highlight based on selection
			points = line.mark_point().encode(
			    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
			)
			if idx == 0:
				# Draw text labels near the points, and highlight based on selection
				text = line.mark_text(align='left', dx=5, dy=-5).encode(
				    text=alt.condition(nearest, str(factor), alt.value(' '))
				)
			else:
				# Draw text labels near the points, and highlight based on selection
				text = line.mark_text(align='left', dx=10, dy=-10).encode(
				    text=alt.condition(nearest, 'Life expectancy at birth, total (years)', alt.value(' '))
				)	
			if idx == 0:
				# Put the five layers into a chart and bind the data
				result_plots.append(alt.layer(line, selectors, points, rules, text))
			else:
				result_plots.append(alt.layer(line, selectors, points, rules, text).properties(height=200))	
			idx += 1
		result_plot = alt.vconcat(result_plots[0], result_plots[1]) 
		st.altair_chart(result_plot, use_container_width=True)
	else:
		st.altair_chart(life_exp, use_container_width=True)

def run_relationship_per_year_all_countries():

	@st.cache
	def dropna_by_feature(df, e_feature, h_feature):
		return df.dropna(how='any', subset=[e_feature, h_feature])

	@st.cache
	def get_by_year(df, year):
		return df[df['Year'] == year]

	st.sidebar.header("Adjust Parameters")

	data, countries = load_merge_data()

	econ_factors = [
			       'GDP per capita (current US$)',
			       'Unemployment, total (% of total labor force)',
			       'Gini',]

	health_factors = ['Current health expenditure (% of GDP)',
				       'Current health expenditure per capita (current US$)',
				       'Life expectancy at birth, total (years)',]

	e_factor = st.sidebar.radio("Economics Factor", (econ_factors))
	h_factor = st.sidebar.radio("Health Factor", (health_factors))

	curr_data = dropna_by_feature(data, e_factor, h_factor)

	max_year = curr_data['Year'].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(curr_data['Year'].unique())), value=max_year)

	curr_data = get_by_year(curr_data, year)
	st.dataframe(curr_data[['Country Name', e_factor, h_factor]].assign(hack='').set_index('hack'))

	# plot a auxilariy life expectancy graph below

	# get max and min y
	max_life = curr_data['Life expectancy at birth, total (years)'].max().item()
	min_life = curr_data['Life expectancy at birth, total (years)'].min().item()

	# double click to clear brush
	brush = alt.selection_interval(encodings=['x'])
	highlight = alt.selection_single(encodings=['color'], on='mouseover', nearest=False, clear="mouseout")

	stripplot = alt.Chart(curr_data).mark_circle(size=50).encode(
		x=alt.X('Life expectancy at birth, total (years):Q', 
			scale=alt.Scale(domain=(min_life, max_life))
		),
		y=alt.Y('jitter:Q',
	        title=None,
	        axis=alt.Axis(values=[0], ticks=True, grid=False, labels=False),
	        scale=alt.Scale(),
	    ),
		color=alt.Color('Country Name', legend=None),
	).transform_calculate(
		# Generate Gaussian jitter with a Box-Muller transform
		jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
	).properties(
		width=700,
		height=50
	).add_selection(brush).transform_filter(highlight)


	# get max and min y
	maxy = curr_data[h_factor].max().item()
	miny = curr_data[h_factor].min().item()
	maxx = curr_data[e_factor].max().item()
	minx = curr_data[e_factor].min().item()
	plot = alt.Chart(curr_data).mark_point().encode(
	    x=alt.X(e_factor, scale=alt.Scale(domain=(minx, maxx))),
	    y=alt.Y(h_factor,
	            scale=alt.Scale(domain=(miny, maxy))),
	    color=alt.Color('Country Name', legend=None),
	    tooltip=alt.Tooltip(['Country Name'])
	).transform_filter(brush).properties(width=700).add_selection(highlight)
	result = alt.vconcat(plot, stripplot)

	st.altair_chart(result, use_container_width=True)

if __name__ == "__main__":
    main()