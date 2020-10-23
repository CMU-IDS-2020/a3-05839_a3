# 05839 Assignment 3

![A screenshot of your application. Could be a GIF.](https://raw.githubusercontent.com/CMU-IDS-2020/a3-05839_a3/master/screenshot.png)

We provide 5 distinct visualizations to help our users understand worldwide and historical patterns of national economy and health.

## Project Goals

National economic status and health level are crucial indicators of a country’s development. Our interactive application aims to tell stories about worldwide and historical patterns of national economy and health, using comprehensive data on various indicators from the World Bank[the World Bank data](https://data.worldbank.org/indicator). With our application, a user can explore the trend of an individual economy or health indicator, the relationship between an economy indicator and a health indicator, as well as a country’s population age distribution. The visualizations, for each of which detailed instructions are provided, should allow a user to explore these trends both temporally and spatially. Through the visualizations, we hope users can get insights into economy and population health among countries over the past few decades, and correlations of economy and health indicators, if any.


## Design

We considered two dimensions when deciding on the five visualizations. First, we considered whether we want to visualize a single variable, or a pair of variables (one economy indicator and one health indicator). Second, we considered whether we want to allow temporal or spatial sliding. The four combinations of these two dimensions, in addition to the data on population age distribution, led to our five visualizations.

### Population Age Distribution

For this visualization, we draw 3 different charts.

First, we plot an area graph of the population age distribution of a particular country in 5 sampled years. Each colored area represents the population structure of the country in one specific year. Since we can set the opacity of each area in the chart, by overlapping those semi-opaque areas, we can present the changes in population structure for a country over years. We have also considered using line charts and multi-bar charts. We settled for the area graph, as viewers could infer the total population by looking at the size of an area, and this is a useful feature that the other options could not provide. For some countries, this area graph can have much overlapping, and it may be difficult for them to examine the exact shape of the areas. We thus added the interaction which allows users to click on the year on the legend and shows only the area chart of a specific year. We hope this interactive visualization could help users to narrow down the range of years they would like to explore.

The population age distribution for one year is typically drawn using a pyramid chart, which in our understanding, combines two bar charts with a shared y-axis. The population age distribution is drawn separately by gender on each side, with the youngest age population group on the bottom, and oldest age group on the top. We have also considered using an area graph as the previous chart.  As most users might have already been familiar with this type of population pyramid graph, we decided to follow this design. We added interactive features that highlight the bar as the mouse moves over the chart. The corresponding bars in the same age range of both genders will also be highlighted for comparison. Tooltips containing the exact data value, in this case, the percentage of the population, will also be shown as the mouse moves over a particular bar.

We also thought that a bar chart of population age distribution not separated by gender would be helpful for users to explore the specific percentage of each age group. We decided to keep the format of this graph the same as the previous one, inheriting all its interactions. We also added where the median age resides in the bar chart so that users can better infer the population distribution.
Having a timeline slider on the side, users can slide and see the population age structure changes for a country overtime. We also provide a drop-down menu for users to select the country he or she wants to explore.

### Life Expectancies & Other Indicators

This visualization contains two parts.

The first one is a line chart of life expectancy at birth over years, where one line corresponds to life expectancy for one country. Since we want to show the general trend in life expectancy in the past few decades, line graphs would fit this purpose perfectly. Not to mention that the default configuration will plot more than 200 countries in the same graph, the line graph is among the few options that would still give us a relatively readable graph. We added interaction to show the country name when the user moves the mouse over a line. This would help users to choose countries with interesting lines to explore. To further aid users in narrowing down exploration scope, we added options so that users could choose to keep only the top 5 or bottom 5 countries in terms of life expectancy in 2017.

The second part of this visualization will be displayed when the user selects several countries from the multi-select box to look at. The user can also specify a particular indicator to look at. The second part contains two line plots of the selected indicator and life expectancy over years, respectively. To keep a coherent design, we choose to use line charts, which is the same as the previous part. Since we are comparing the general trend of one indicator to life expectancy, a line graph is a good visual encoding for this task. These two plots share the same x-axis, and as the user moves the mouse in the upper plot, a vertical line will move alongside, showing the y values of the same year (x value). This interaction enables the user to look at not only the general trend and relative differences if multiple countries are selected, but also allows the user to compare the exact corresponding values at the same time.

### Health & Economy Interaction, per Year

This visualization contains a combination of one scatter plot and one stripplot. In this section, we have three variables to present: a health indicator, a economy indicator, and life expectancy; we would like to compare how values of a health indicator and a economy indicator distribute among all countries in a specific year; we also want to see, by positioning countries on a 2 dimensional graph, how is a country’s relative position relates to its relative position in the life expectancy in the world. We added interaction which users can select one health indicator and one economy indicator to explore. Users can also slide with the time slider to choose a specific year to look at.

We have the scatter plot for the selected pair of health/economy indicators. Since one country’s data is independent of other countries’, scatter plot is a quite reasonable choice. We have also considered a 2d bubble chart, which builds on the existing scatter plot, and adjusts each dot size according to the life expectancy. After experimenting with it, we found that with a large number of countries, bubbles tend to clump together where larger ones overlap smaller ones and become a mess. Also the large number of data points make the relative size of bubbles hard to tell, even if for some of the “outlier” dots.  In the end, we decided to add a second strip plot with jitters to plot the single variable: life expectancy.

To help users locate the same country from the two plots simultaneously, we added interaction to the scatter plot, so that when the mouse moves over a data point, it will show the user the name of the country with the indicator values, and the corresponding data point of the country on the strip plot will also be highlighted.

Users might want to explore questions like “What are the indicator values and relative positions for countries with high life expectancy?” For users who want to explore a subset of the data, we added another interaction that allows the user to select a life expectancy interval on the strip plot, and the scatter plot will filter out all countries that are not in the interval. Users can move the selected area on the strip plot or reset and re-select another interval.

### Health & Economy Interaction, per Country

At first, we considered a scatter plot for a selected pair of health/economy indicators. However, that would not enable a user to easily gain an understanding of temporal patterns. Recall that our goal for each of the four visualizations (except for the population age distribution) is to allow either temporal or spatial exploration. Thus, we decided on line plots for the pair. The most natural way for us to differentiate two lines is to use coloring.

As indicated by the visualization title, we allow a user to first choose a country, and then an economy indicator and a health indicator. We think that dropdown menus are the most effective widget, as all three variables are nominal.
Finally, we think that a user might want to zoom in to focus on trends in a specific period of time. Therefore, we enabled our visualization to be zoomable and draggable.

### Health/Economy over the World

Since the goal for this visualization is to show patterns of a single variable across countries at a particular time, we think that a map whose coloring corresponds to variable magnitude can best achieve our purpose. It provides a direct view of the global trend. 

As indicated by the visualization title, we allow a user to first choose an indicator and then a year. Again, since the set of indicators is nominal and time discrete, we used a dropdown menu for indicators and a slider for time.

Finally, we think that a user might be interested in knowing the exact value of the indicator for a specific country on the map, so we allow a user to read more information when moving the mouse over the map. Initially, we considered displaying details of a country on a sidebar next to the map, but we discovered that it would negatively impact the map display because of the already limited page width.


## Development

We started this project with brainstorming on possible topics and questions together in a meeting. After deciding on the main topic and scope of the project, we each individually came up with ideas on how to approach this question. In a second meeting, we shared our ideas and decided on 5 final visualizations that we have listed above. We went off and implemented those visualizations. The first three of the five visualizations were accomplished by Ling, and the last two by Hongyuan. Although each person was in charge of specific visualizations, we collaborated with each other during the development process by sharing code templates and design ideas. We also reviewed each other’s implementation and writeup for the application. After we have finished developing our features, we collaboratively produced this writeup. 
Besides online meetings of approximately 1.5 hours, Ling spent 15 hours on developing her features, and Hongyuan spent 12 hours. Hongyuan also contributed in proof reading the context in the web application. For Ling, experimenting with different visualization options and developing the features took the most time.  For Hongyuan, collecting and merging data (health/economy data joined with country code, average latitude and longitude), as well as debugging the interactive features took the most time.

