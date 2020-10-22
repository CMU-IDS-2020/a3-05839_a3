import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
import math


OVERVIEW = "Overview"
POPU_DIST = "Population Age Distribution"
VAR_RELATIONSHIP_PER_COUNTRY = "Health & Economy Interaction, per Country"
ONE_VAR_ACROSS_REGION = "Health / Economy over the World"
SINGLE_FACTOR_OVER_TIME = 'Life Expectancies & Other Indicators'
POINT2_PLACEHOLDER = 'Health & Economy Interaction, per Year'
# locations of data
HEALTH_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/health.csv"
OTHER_DATA_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/merged_data_country_only_with_id_lat_lon.csv"
MERGED_URL = "https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/data/merged_data_country_only.csv"
WORLD_MAP_URL = "https://raw.githubusercontent.com/vega/vega-datasets/master/data/world-110m.json"
# locations of markdowns


def main():
	# Add a selector for the app mode on the sidebar.
	st.sidebar.title("Navigation")
	vis_topic = st.sidebar.radio("",
		(str(OVERVIEW), str(POPU_DIST), str(SINGLE_FACTOR_OVER_TIME) , str(POINT2_PLACEHOLDER), str(VAR_RELATIONSHIP_PER_COUNTRY), str(ONE_VAR_ACROSS_REGION)))
	if vis_topic == OVERVIEW:
		# Render main readme, placeholder
		readme_text = st.markdown("readme.md")
	elif vis_topic == POPU_DIST:
		st.title(POPU_DIST)
		run_popu_dist()
	elif vis_topic == VAR_RELATIONSHIP_PER_COUNTRY:
		st.write(VAR_RELATIONSHIP_PER_COUNTRY)
		run_var_relationship_per_country()
	elif vis_topic == ONE_VAR_ACROSS_REGION:
		st.write(ONE_VAR_ACROSS_REGION)
		run_one_var_across_region()
	elif vis_topic == SINGLE_FACTOR_OVER_TIME:
		st.title(SINGLE_FACTOR_OVER_TIME)
		run_trend_over_time()
	elif vis_topic == POINT2_PLACEHOLDER:
		st.title(POINT2_PLACEHOLDER)
		run_relationship_per_year_all_countries()


@st.cache
def load_data(url):
    data = pd.read_csv(url, header=0, skipinitialspace=True)
    data = data[data['Year'] <= 2017]
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
def load_other_data():
	df, countries = load_data(OTHER_DATA_URL)
	df['id'] = df['id'].astype(str)
	df['id'] = df['id'].str.zfill(3)
	econ_indicators = df.columns[[3, 6, 8]]
	health_indicators = df.columns[[4, 5, 7]]
	return df, countries, econ_indicators, health_indicators


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
	# takes in a dataframe and list of country names
	# this function will return a dataframe with only data from the specified countries
	sub_df = df[df['Country Name'].isin(selected_countries)]
	return sub_df


@st.cache
def dropna_by_feature(df, features):
	# takes in a dataframe and list of features to checkon,
	# this function will drop rows which has np.nan in any of the features specifed
	return df.dropna(how='any', subset=features)

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

	@st.cache
	def get_only_tens(country_df):
		years = list(np.sort(country_df['Year'].unique()))
		# get selection interval
		interval = math.floor(len(years) / 5)
		if interval == 0:
			only_ten = country_df
		else:
			temp = []
			idx = len(years) - 1
			count = 0
			while idx > 0 and count < 5:
				temp.append(years[idx])
				idx -= interval
				count += 1
			only_ten = country_df[country_df['Year'].isin(temp)]
		return only_ten	

	@st.cache
	def get_only_ten_general(country_df, age_ranges):
		only_ten = get_only_tens(country_df)
		values2 = []
		years2 = []
		indexes = []
		ages = []
		for _, data_row in only_ten.iterrows():
			for i in range(len(age_ranges)):
				values2.append(data_row['Population ages {} (% of total population)'.format(str(age_ranges[i]))] * data_row['Population, total'])
				years2.append(data_row['Year'])
				indexes.append(i)
				ages.append(age_ranges[i])
		overall_data = pd.DataFrame({'Idx': indexes, 'Population Ages': ages, 'Year': years2, 'Population': values2})
		return overall_data  	

	st.markdown('''
		## Health through the lens of population age distribution

		In this section, we will look at population age distribution of a specific country. 
		Though this data might be affected by other factors like wars/regional conflicts, and willingness to birth,
		it is still a good indicator of population health and health service quality in a country.

		We have observed a general demographic shift in the past few decades, where the percentage of young dependents drops,
		and mid-ages increase [1]. Since world population has also been skyrocketting [2] and fertility rate dropping [3] in the same time frame, 
		the changes in the population distribution would suggest that population increases usually for all age groups, 
		and population with mid to old ages has the steepest upward trend. We are now having less 
		mortalities from some health threats like infectious and parasitic diseases which haunted the world in the past; 
		mortality rate also decreases for major diseases [3].

		The changes in the population age distribution, where mid-to-old age population has a smaller
		gap with young population, suggest that we are having a healthier population [1].

		## Let's look at the data

		You are free to adjust the parameters in the left side bar now,
		but we will also walk you through these options through the explanations below.

		You can select a country from **drop down menu** in the side bar. 

	''')

	# load health data
	health_df, countries = load_health_data()
	health_grouped = data_group_by_country(health_df)

	st.sidebar.header("Adjust Parameters")

	country = st.sidebar.selectbox("Country", countries)
	country_df = health_grouped[country]

	max_year = country_df['Year'].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(country_df['Year'].que())), value=max_year)
	by_gender = st.sidebar.checkbox('View By Gender', value=False)

	# # plot based on the country, hack for not displaying the column index
	# st.dataframe(country_df.assign(hack='').set_index('hack'))

	# plot the histogram base on country and year
	row = country_df.loc[country_df['Year'] == year]

	percentage_max = get_total_ymax(country_df, health_df)
	age_ranges_overall = ['0-14', '15-19', '20-24', '25-29', '30-34', '35-39', '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75-79', '80 and above']
	values_overall = []
	for r in age_ranges_overall:
		values_overall.append(row['Population ages {} (% of total population)'.format(r)].item())
	curr_data_overall = pd.DataFrame({'Population Ages': age_ranges_overall, '% of Total Population': values_overall})

	# the layered area graph
	only_ten = get_only_ten_general(country_df, age_ranges_overall)
	# highlight selector
	keep_one = alt.selection_single(fields=['Year'], bind='legend', nearest=False, empty='all')

	area_graph = alt.Chart(only_ten).mark_area(opacity=0.4).encode(
	    x=alt.X('Idx', title=None, axis=alt.Axis(ticks=True, grid=True, labels=False)),
	    y=alt.Y('Population', stack=None),
	    color=alt.Color("Year:N", scale=alt.Scale(scheme='lightmulti')),
	    opacity=alt.condition(
	    	keep_one,
	    	alt.value(0.4),
	    	alt.value(0)
	    )
	).add_selection(keep_one)


	xaxis = alt.Chart(only_ten).mark_point().encode(
	    x=alt.X('Population Ages', axis=alt.Axis(ticks=False, grid=False)),
	    opacity=alt.value(0),
	)

	st.altair_chart(alt.layer(xaxis, area_graph), use_container_width=True)

	st.markdown('''
		The above graph visualizes the population age distribution of your selected country. 
		The x-axis represents the age groups, in the order of increasing age;
		the y-axis represents the number of people in this age group.

		To see the general demographic changes of your selected country over years with ease,
		the graph only shows data from 5 separate years, chosen with a nearly fixed interval. 

		You can click on the legend to see area plot from a specific year. 
		Clicking on other parts of the graph will reset the selection and show graphs of all five years.
		



		For the specific country you have just selected, you can also choose to look at a specific year
		by sliding the **slider** on the side bar. You will have more options to choose from, other than the 
		5 sample years on the area graph.
	''')

	# get median
	median = curr_data_overall['% of Total Population'].sum() / 2.0
	p_agg = 0.0
	for _, data_row in curr_data_overall.iterrows():
		prev_p_agg = p_agg
		p_agg += data_row['% of Total Population']
		if p_agg >= median:
			median_age_range = data_row['Population Ages']
			break			

	# highlight selector
	highlight = alt.selection_single(on='mouseover', fields=['Population Ages'], nearest=False, clear="mouseout")

	hist = alt.Chart(curr_data_overall).mark_bar().encode(
	    y=alt.Y('% of Total Population',
	    	scale=alt.Scale(domain=(0, percentage_max))),
	    x='Population Ages',
	    color=alt.condition(
	        ~highlight,
	        alt.Color('Population Ages:O', scale=alt.Scale(scheme='greens'), legend=None),
	        alt.value('orange'),     # which sets the bar orange.
	    ),
	    tooltip=['Population Ages', '% of Total Population']
	).add_selection(highlight).interactive()

	hist_background = alt.Chart(curr_data_overall).mark_bar().encode(
	    y=alt.Y('background_height:Q',
	    	scale=alt.Scale(domain=(0, percentage_max)),
	    	title='% of Total Population'),
	    x=alt.X('Population Ages'),
	    color=alt.condition(
	        alt.datum['Population Ages'] == median_age_range,
	        alt.value('lightgray'),
	        alt.value('white')
	    ),
	    opacity=alt.condition(
	        alt.datum['Population Ages'] == median_age_range,
	        alt.value(0.2),
	        alt.value(0.0)
	    ),
	).transform_calculate(
		background_height = "100"
	)

	text = alt.Chart(curr_data_overall).mark_text(
	    align='left',
	    baseline='middle',
	    dy=-10,
	    dx=-15
	).encode(
		y=alt.Y('% of Total Population'),
	    x='Population Ages',
		text=alt.condition(alt.datum['Population Ages'] == median_age_range, alt.value('median'), alt.value(' '))
	)
	st.altair_chart(alt.layer(hist_background, hist, text), use_container_width=True)

	st.markdown('''
		This is a bar chart displaying the detailed population distribution of your selected country in one specific year.
		Same as the previous graph, the x-axis shows the population age group, and the y-axis show the percentage.
		The y-axis upper limit is the max age group percentage of this country. By fixing the scale of y-axis, 
		we are hoping that you can more clearly see the percentages' change over time as you are sliding the time
		slider.

		If the median age falls in an age group, the corresponding bar will have a darker background and the word 'median' 
		on top. The median may help you get a better concept of the overall distribution, as this graph can be highly screwed
		towards the origin.

		By moving your mouse over a bar, you will see the exact percentage of this age group in the total population. 
		This bar will also be highlighted orange. You can zoom and rescale the chart with two fingers; drag and hold 
		on the graph canvas will shift the plotting area. Double clicking on the graph will reset the graph.

		You can view population distribution of the selected year of this country by gender. By checking the
		'View by Gender' **checkbox** on the side bar, you can view the population distribution pyramid graph.
	''')

	if by_gender:
		age_ranges = ['80 and above', '75-79', '70-74', '65-69', '60-64', '55-59', '50-54', '45-49', '40-44', '35-39', '30-34', '25-29', '20-24', '15-19']
		male_values = []
		female_values = []
		for r in age_ranges:
			male_values.append(row['Population ages {}, male (% of male population)'.format(r)].item())
			female_values.append(row['Population ages {}, female (% of female population)'.format(r)].item())
		curr_data = pd.DataFrame({'Population ages': age_ranges, '% of Male Population': male_values, '% of Female Population': female_values})
		
		# write current data
		#st.dataframe(curr_data.iloc[::-1].assign(hack='').set_index('hack'))

		maxx = curr_data['% of Male Population'].max()
		if curr_data['% of Female Population'].max().item() > maxx:
			maxx = curr_data['% of Female Population'].max()

		base2 = alt.Chart(curr_data).properties(width=300)
		# highlight selector
		highlight2 = alt.selection_single(on='mouseover', fields=['Population ages'], nearest=False, clear="mouseout")

		left = base2.encode(
		    y=alt.Y('Population ages:O', axis=None, sort=alt.EncodingSortField(order='ascending')),
		    x=alt.X('% of Female Population',
		            title='% of Female Population',
		            sort=alt.SortOrder('descending'),
		            scale=alt.Scale(domain=(0, maxx))),
		    color=alt.condition(
		        ~highlight2,
		        alt.Color('Population ages:O', scale=alt.Scale(scheme='redpurple'), legend=None),
		        alt.value('orange'),     # which sets the bar orange.
		    ),
		    tooltip=['Population ages', '% of Female Population']
		).mark_bar().properties(title='Female').add_selection(highlight2)

		middle = base2.encode(
		    y=alt.Y('Population ages:O', axis=None, sort=alt.EncodingSortField(order='ascending')),
		    text=alt.Text('Population ages'),
		).mark_text().properties(width=40)

		right = base2.encode(
		    y=alt.Y('Population ages:O', axis=None, sort=alt.EncodingSortField(order='ascending')),
		    x=alt.X('% of Male Population',
		            title='% of Male Population',
		            sort=alt.SortOrder('ascending'),
		            scale=alt.Scale(domain=(0, maxx))),
		    color=alt.condition(
		        ~highlight2,
		        alt.Color('Population ages:O',scale=alt.Scale(scheme='blues'), legend=None),
		        alt.value('orange'),     # which sets the bar orange.
		    ),
		    tooltip=['Population ages', '% of Male Population']
		).mark_bar().properties(title='Male').add_selection(highlight2)

		bihist=alt.concat(left, middle, right, spacing=2).resolve_scale(color='independent')
		st.altair_chart(bihist, use_container_width=True)

		st.markdown('''
			This is a classic age structure pyramid graph. The left side of the graph is the age population 
			distribution of female in the selected year of this country. By moving your mouse over a bar, 
			you will see the exact percentage of this age group in its gender population. 
			This bar and the bar of the same age group from the other gender will also be highlighted orange.
		''')

	st.markdown('''
		
		### References
		[1]
		Hannah Ritchie (2019) - "Age Structure". 
		Published online at OurWorldInData.org. 
		Retrieved from: 'https://ourworldindata.org/age-structure' [Online Resource]

		[2]
		Max Roser, Hannah Ritchie and Esteban Ortiz-Ospina (2013) - "World Population Growth". 
		Published online at OurWorldInData.org. 
		Retrieved from: 'https://ourworldindata.org/world-population-growth' [Online Resource]

		[3]
		Global Health and Aging [PDF]. (2011, October). The World Health Organization.
	''')	


def run_var_relationship_per_country():
	st.markdown('''
	## How is an economy indicator associated with a health indicator for a specific country?
	
	As argued in existing literature [1], "in the long term, growing economies are associated with longer and healthier lives," whereas
	"in the short term, that may not be the case—economic booms can boost mortality rates and busts can reduce them." Thus, it is particularly
	important and interesting to visualize the trends in economy and health of a country.
	

	In this section, we explore the relationship between any pair of a national economy indicator and a national health indicator over time. 
	
	## Let's look at the data
	
	Using the sidebar, you are free to choose 

	1. a specific country, 
	2. a economy indicator (one of Gini, GDP per capita, and unemployment rate),
	and finally 
	3. a health indicator (one of health expenditure as % of GDP, health expenditure per capita, and life expectancy).
	
	This way, you can easily visualize the interaction between your selected pair of indicators. Each plot will have two y-axes correponding to each of the indicator.
	
	Our visualization is interactive. You can check out the specific value of an indicator in a specific year by moving your mouse over the desired point on a line.
	In addition, you can drag the graph to adjust the time range. Finally, you can use your touchpad to zoom in or zoom out. Again, double clicking will reset the plot.
	
	Please note that the original data has many missing entries. When there is no data for either indicator in the selected pair for the selected country, 
	we cannot generate a visualization for you, as indicated by "Data Not Available." Please try another pair of indicators.
	''')
	df, countries, econ_indicators, health_indicators = load_other_data()
	other_data_df = df.copy()
	other_data_df['Year'] = pd.to_datetime(other_data_df['Year'], format='%Y')
	st.sidebar.header("Adjust Parameters")

	country = st.sidebar.selectbox("Country", countries)
	country_df = other_data_df[other_data_df["Country Name"] == country]

	econ_indicator = st.sidebar.selectbox("Economy Indicator", econ_indicators, index = 1)
	health_indicator = st.sidebar.selectbox("Health Indicator", health_indicators, index = 2)
	bi_var_df = country_df[["Year", econ_indicator, health_indicator]]

	if bi_var_df.dropna().empty:
		st.write("Data Not Available")
	else:
		nearest1 = alt.selection(type='single', nearest=True, on='mouseover',
								fields=['Year'], empty='none')
		nearest2 = alt.selection(type='single', nearest=True, on='mouseover',
								fields=['x'], empty='none')
		base = alt.Chart(bi_var_df).encode(
			alt.X('Year:T', axis=alt.Axis(title='Year', format=("%Y")))
		)
		line1 = base.mark_line(color='#5276A7').encode(
			alt.Y(econ_indicator,
				  axis=alt.Axis(title=econ_indicator, titleColor='#5276A7')),
				  tooltip=[alt.Tooltip(econ_indicator, title=econ_indicator)]
		).add_selection(nearest1).interactive()
		line2 = base.mark_line(color='#57A44C').encode(
			alt.Y(health_indicator,
				  axis=alt.Axis(title=health_indicator, titleColor='#57A44C')),
			      tooltip=[alt.Tooltip(health_indicator, title=health_indicator)]
		).add_selection(nearest2).interactive()
		line_plot = alt.layer(line1, line2).resolve_scale(
			y='independent'
		)
		st.altair_chart(line_plot, use_container_width=True)
	st.markdown('''
				### References
				[1]
				Austin B. Frakt (2018) - "How the Economy Affects Health". JAMA. 319(12):1187–1188. doi:10.1001/jama.2018.1739
			''')

def run_one_var_across_region():
	st.markdown('''
	## What's the world-wide trend of a particular indicator?
	
	In this section, we provide a snapshot of the world-wide trend of a particular indicator in the form of a world map. 
	The previous sections allow you to gain an understanding in either trends of single/double variable(s) over time or trends of double variables across countries. 
	This section provides a complementary visualization for trend of a single variable across countries.
	
	In this age, regional integration is not uncommon; we would expect a country to have similar economy status or health level to its neighboring countries.
	Indeed, as argued in [1], "countries with open, large, and more developed neighboring economies grow faster than those with closed, smaller, and less developed neighboring economies."
	
	## Let's look at the data
	
	To start, first select an economy/health indicator of interest. Then, use the time slider to select a year of interest. If any data is available for the selected indicator and year, you will see
	a world map whose coloring corresponds to magnitude of the indicator. To check out the indicator value for a particular country, move your mouse over the approximate location of the country on the map.
	Slide over time to check out how the world-wide trend changed over time!
	''')
	countries = alt.topo_feature(WORLD_MAP_URL, 'countries')
	other_data_df, _, econ_indicators, health_indicators = load_other_data()
	st.sidebar.header("Adjust Parameters")

	indicator = st.sidebar.selectbox("Health / Economy Indicator", list(econ_indicators) + list(health_indicators))
	uni_var_df = other_data_df[["Country Name", "Year", indicator, 'id', 'Latitude (average)', 'Longitude (average)']]

	no_na_df = uni_var_df.dropna()
	max_year = no_na_df["Year"].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(no_na_df['Year'].unique())), value=max_year)
	uni_var_one_year_df = uni_var_df[uni_var_df["Year"] == year]

	if uni_var_one_year_df.dropna().empty:
		st.write("Data Not Available")
	else:
		map = alt.Chart(countries).mark_geoshape().encode(
			color=alt.Color(indicator+':Q',
				scale=alt.Scale(scheme="yellowgreenblue"),
				legend=alt.Legend(orient='top', titleLimit=800, titleOrient='left'))
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
		map = (map + points).properties(height=500)
		st.altair_chart(map, use_container_width=True)
	st.markdown('''
	### References
	
	[1] Athanasios Vamvakidis (1998) - "Regional Integration and Economic Growth". The World Bank Economic Review, Volume 12, Issue 2, May 1998, Pages 251–270, https://doi.org/10.1093/wber/12.2.251''')


def run_trend_over_time():
	st.markdown('''
		## How is life expectancies associated with health indicators and economics indicators?


		Having a healthy lifestyle can increase the life expectancy [1], and the trend in line expectancy
		over time can refect the changes in population health conditions, health services adequacy.

		In this seciton, we will explore the relationship between life expectancy and health expenditures
		and economics indicators. 

		## Let's see the data

		To compare data for specific countries, can choose multiple countries in the **multi-selection box** on the left side bar. 
		If no countries are selected, we will show you a graph of life expectancy over time for all countries.

		Once you have selected one or more countries to focus on, you can choose an a additional indicator to explore its relationship with life expectancy over time, while
		comparing among multiple countries from the **drop down menu** in the side bar.
	''')
	data_cached, countries = load_merge_data()
	data = data_cached.copy()
	data['Year'] = pd.to_datetime(data['Year'], format='%Y')

	# drop box to select one variable to view
	st.sidebar.header("Adjust Parameters")

	factors = [
       'Current health expenditure (% of GDP)',
       'Current health expenditure per capita (current US$)',
       'GDP per capita (current US$)',
       'Unemployment, total (% of total labor force)',
       'Gini',]

	factor = st.sidebar.selectbox("Additional Factors", factors)

	selected_countries = st.sidebar.multiselect('Select Countries to Compare', countries)

	# plot factor countries over time
	if selected_countries:

		curr_df = keep_only_selected_countries(data, selected_countries)

		curr_df = dropna_by_feature(curr_df, [factor, 'Life expectancy at birth, total (years)'])

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
		st.markdown('''
			The above graph consists of two line charts. The upper one displays a line chart of your selected 
			indicator for the selected countries over time. The lower chart, on the same time scale, displays 
			the life expectancies of those countries. You can compare the trend and shape of your selected factor
			with the line of life expectancy of one country; or you can compare the impact on life expectancy of difference in 
			your selected indicator for several countries.

			To make the comparison meaningful, the graph only shows a time range which we have both life expectancy
			and the selected indicator data collected for the specified countries.

			You can move your mouse on the upper graph, a verticle line displays the nearest year that your mouse 
			points to, and the corresponding data points will be exaggrated with the exact y values to the right of the 
			data point. The values are printed in the same color as its corresponding line.
		''')

	else:
		country_filter = st.radio('', ('All', 'Top 5 as of 2017', 'Bottom 5 as of 2017'))
		if country_filter == 'All':
			countries_keep = countries
		elif country_filter == 'Top 5 as of 2017':
			countries_keep = data[data['Year'] == pd.to_datetime('2017', format='%Y')].sort_values('Life expectancy at birth, total (years)',ascending = False).head(5)['Country Name']
		else:
			countries_keep = data[data['Year'] == pd.to_datetime('2017', format='%Y')].sort_values('Life expectancy at birth, total (years)').head(5)['Country Name']

		data = keep_only_selected_countries(data, countries_keep)
		# always plot the life expectancy
		life_exp = alt.Chart(data).mark_line(size=4).encode(
			x=alt.X('Year:T', 
					 scale=alt.Scale(domain=(
					 	pd.to_datetime('1960', format='%Y'),
					 	pd.to_datetime('2017', format='%Y')
					 )),
					 axis = alt.Axis(title = 'Year', format = ("%Y"))),
		    y=alt.Y('Life expectancy at birth, total (years)', scale=alt.Scale(domain=(0, 90))),
		    color='Country Name',
		    tooltip=['Country Name']
		)
		st.altair_chart(life_exp.properties(height=450), use_container_width=True)
		st.markdown('''
			The above is a line graph of life expectancy at birth over time, where each line is a different country.
			Most of the lines are mangled together as there are so many countries in the world. Instead of looking at the 
			lines of specific countries, we hope to provide you with a idea of a general increasing trend in life expectancy in 
			the recent years in the world. 

			If you find a particular line especially interesting, you will be able to see the name of the country 
			corresponding to the line by moving your mouse over it.

			We have provides two filter options to help you narrow down your exploration scope. The default 'All' will
			show all countries on the graph; 'Top 5 as of 2017' will only keep 5 countries or regions with highest
			life expectancy in 2017; similarly, 'Bottom 5 as of 2017' will only keep 5 countries or regions with least
			life expectancy in 2017.
		''')

	st.markdown('''
		### References
		[1]
		Li, Y., Pan, A., Wang, D. D., Liu, X., Dhana, K., Franco, O. H., . . . Hu, F. B. (2018). 
		Impact of Healthy Lifestyle Factors on Life Expectancies in the US Population. 
		Circulation, 138(4), 345-355. doi:10.1161/circulationaha.117.032047
	''')

def run_relationship_per_year_all_countries():

	@st.cache
	def get_by_year(df, year):
		return df[df['Year'] == year]


	st.markdown('''
		## How is an economy indicator associated with a health indicator among diffrent countries?
		
		As argued in existing literature [1], "in the long term, growing economies are associated with longer and healthier lives," whereas
		"in the short term, that may not be the case—economic booms can boost mortality rates and busts can reduce them." Thus, it is particularly
		important and interesting to visualize the trends in economy and health of a country.

		In this section, we explore the relationship between any pair of a national economy indicator and a national health indicator for a specific year,
		among all countries. We also hope to show you if relationship between any of the two indicators exhibits some correlations to 
		the life expactancy.
		
		## Let's look at the data
		
		Using the sidebar, you are free to choose 

		1. a specific year, 
		2. a economy indicator (one of Gini, GDP per capita, and unemployment rate),
		and finally 
		3. a health indicator (one of health expenditure as % of GDP and health expenditure per capita).
		
		This way, you can easily visualize the interaction between your selected pair of indicators.
		
		You can select a specific year to explore with the **slider** on the left side bar.
	''')

	st.sidebar.header("Adjust Parameters")

	data, countries = load_merge_data()

	econ_factors = [
			       'GDP per capita (current US$)',
			       'Unemployment, total (% of total labor force)',
			       'Gini',]

	health_factors = ['Current health expenditure (% of GDP)',
				       'Current health expenditure per capita (current US$)',
				       #'Life expectancy at birth, total (years)',
				       ]

	e_factor = st.sidebar.radio("Economics Factor", (econ_factors))
	h_factor = st.sidebar.radio("Health Factor", (health_factors))

	curr_data = dropna_by_feature(data, [e_factor, h_factor])

	max_year = curr_data['Year'].max().item()
	year = st.sidebar.select_slider("Year", options=list(np.sort(curr_data['Year'].unique())), value=max_year)

	curr_data = get_by_year(curr_data, year)
	#st.dataframe(curr_data[['Country Name', e_factor, h_factor]].assign(hack='').set_index('hack'))

	# plot a auxilariy life expectancy graph below

	# get max and min y
	max_life = curr_data['Life expectancy at birth, total (years)'].max().item()
	min_life = curr_data['Life expectancy at birth, total (years)'].min().item()

	# double click to clear brush
	brush = alt.selection_interval(encodings=['x'])
	highlight = alt.selection_single(encodings=['color'], on='mouseover', nearest=False, clear="mouseout")

	stripplot = alt.Chart(curr_data).mark_circle(size=40).encode(
		x=alt.X('Life expectancy at birth, total (years):Q', 
			scale=alt.Scale(domain=(min_life, max_life))
		),
		y=alt.Y('jitter:Q',
	        title=None,
	        axis=alt.Axis(values=[0], ticks=False, grid=False, labels=False),
	        scale=alt.Scale(),
	    ),
		color=alt.Color('Country Name', legend=None),
		opacity=alt.condition(
			highlight,
			alt.value(0.7),
			alt.value(0.1)
		)
	).transform_calculate(
		# Generate Gaussian jitter with a Box-Muller transform
		jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
	).properties(
		width=700,
		height=50
	).add_selection(brush)
	#.transform_filter(highlight)


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
	    tooltip=alt.Tooltip(['Country Name', e_factor, h_factor])
	).transform_filter(brush).properties(width=700).add_selection(highlight)
	result = alt.vconcat(stripplot, plot)

	st.altair_chart(result, use_container_width=True)

	st.markdown('''
		The above graph consists of two charts. 
		The upper chart displays a one dimensional graph of life expectancy (we added some jitters to the vertical
		position of each data point, so that they are not clumped together).
		The lower one displays a scatter plot of your selected indicators in the specific year for all countries. 
		Its x-axis corresponds to your selected economics indicator, and the y axis corresponds to your selected 
		health indicator.
		For both subgraph, a dot represent one particular country. 

		By moving your mouse on a specific dot (a specific country) on the lower chart, the name of the country, its exact values 
		for the two indicators will be shown. Its corresponding life expectancy dot will be hightlighted in the 
		upper chart. You can compare its relative position in both graph among all data points. 

		You can also hold and drag to select a life expectancy interval in the upper graph. Only countries which has 
		life expectancy at birth in this interval in the selected year will be shown on the lower chart. If you have 
		already had an selection interval (shown with a gray backgroud), you can hold and drag the selection interval
		to move it around, the lower chart will reflect the change while you shift the selection interval. Double clicking
		on the upper chart will reset the selection interval.


		### References
		[1]
		Austin B. Frakt (2018) - "How the Economy Affects Health". JAMA. 319(12):1187–1188. doi:10.1001/jama.2018.1739
	''')

if __name__ == "__main__":
    main()