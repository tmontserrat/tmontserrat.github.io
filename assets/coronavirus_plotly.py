import requests
import json
from datetime import datetime, date, timedelta
import plotly.graph_objects as go
from plotly import offline

# Graphs to show the evolution of pandemic in Spain. 
today = datetime.today()
begining_date = datetime.strptime('2020-02-01', "%Y-%m-%d")
# Ref: https://es.stackoverflow.com/questions/259242/restar-dos-fechas-que-
# est%C3%A1n-en-forma-de-cadenas-str
last_days = round((today - begining_date) / timedelta(days=1))

# Make an API call and store the response. 
url = f'https://disease.sh/v3/covid-19/historical/Spain%2C%20France%2C%20Portugal%2C%20Italy%2C%20Germany?lastdays={last_days}'
r = requests.get(url)
print(f"Status code: {r.status_code}")

response_list = r.json()

readable_file = 'data/readable_coronavirus.json'
with open(readable_file, 'w') as f:
    json.dump(response_list, f, indent=4)

# Data dicts
list_index = 0
y_values = []
x_values = []
countries = []
for country_data in response_list:
    data = response_list[list_index]
    countries.append(data['country'])
    cases_dicts = data['timeline']['cases']

    # Make an API call and store the country population.
    name_country = data['country'] 
    url = f'https://restcountries.eu/rest/v2/name/{name_country.lower()}'
    c = requests.get(url)
    print(f"Status code: {c.status_code}")

    country_data = c.json()
    population = country_data[0]['population']

    # Pull acumulative number of cases each day
    number_cases = []
    for total_cases in cases_dicts.values():
        number_cases.append(int(total_cases))

    # Pull the dates
    dates = []
    for date in cases_dicts.keys():
        current_date = datetime.strptime(date, "%m/%d/%y")
        dates.append(current_date)

    # Calculate new cases per day
    new_cases = []
    index = 0
    for cases in number_cases:
        if index - 1 < 0:
            index += 1
            continue 
        else:
            new_cases.append(number_cases[index] - number_cases[index-1])
        index += 1
    
    # Calculate new cases per 1000 thousand people
    index = 0
    for cases in new_cases:
        new_cases[index] = (cases/population)*100000
        index += 1

    # Calculate last 7 days new cases mean
    mean_seven_days = []
    index = 0
    count = 1
    for mean in range(len(new_cases)-7):
        mean_seven_days.append(round(sum(new_cases[index:(6+count)])/len(new_cases[index:(6+count)])))
        index += 1
        count += 1
    # Change wrong mesures for zeros
    index = 0
    for value in mean_seven_days:
        if value < 0:
            value = 0
            mean_seven_days[index] = 0
        index += 1

    x_values.append(dates[8:])
    
    y_values.append(mean_seven_days)
    list_index += 1

# Make visualization. 
index = 0
fig = go.Figure()
for y_value in y_values:
    fig.add_trace(go.Scatter(
        x=x_values[index], y=y_values[index],
        mode='lines',
        name=countries[index],
        # Ref: https://community.plotly.com/t/plotly-hovertemplate-
        # date-time-format/39944/5
        hovertemplate='Date: %{x|%Y/%m/%d}'
            '<br>New cases per 100,000 people: %{y}')),
    fig.update_layout(
        yaxis = dict(
        exponentformat='none',
        separatethousands=True,
        title='New cases per 100,000 people'
        ),
        title={
            'text': 'COVID-19: Evolution in several european countries',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    index += 1

offline.plot(fig, filename='covid_evolution.html')