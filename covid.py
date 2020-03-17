"""
Created: 09/03/2020
Git: https://github.com/V-def/covid
Display graphs: https://covid19.cassayre.me/
"""

import xlrd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os


# function that convert the file (in xls) into a python list
def xls_list(name):
    book = xlrd.open_workbook(name, encoding_override="cp1251")
    sheet = book.sheet_by_index(0)

    n_rows = sheet.nrows
    n_cols = sheet.ncols

    rows = []
    for i in range(1, n_rows):  # skip header
        row = []
        for j in range(n_cols):
            v = sheet.cell_value(i, j)
            if j == 0:  # date
                v = datetime(*xlrd.xldate_as_tuple(v, book.datemode)).strftime('%d/%m/%Y')
            row.append(v)
        rows.append(row)

    return rows


# create a list of all the dates between first case and now (used for the x-axis)
def create_date_list():
    date_disp_list = []
    date_raw_list = []
    date_time_obj = datetime.strptime(date_first_case, '%d/%m/%Y')
    date_tomorrow = datetime.today() + timedelta(1)

    while date_time_obj.strftime('%d/%m/%Y') != date_tomorrow.strftime('%d/%m/%Y'):
        date_disp_list.append(date_time_obj.strftime("%d %b"))
        date_raw_list.append(date_time_obj.strftime('%d/%m/%Y'))
        date_time_obj = date_time_obj + timedelta(1)
    return date_disp_list, date_raw_list


# create list of country
def create_country_list():
    k = len(data)
    country_list_number = []
    country_number_dict = {}
    country_geold_dict = {}
    country_union_dict = {}
    z = 0
    for y in range(k-1):
        if data[y][data_dict["GeoId"]] == \
                data[y + 1][data_dict["GeoId"]] != data[y - 1][data_dict["GeoId"]]:
            z = y
            country_list_number.append(y)

            country_geold_dict.update(
                {data[y][data_dict["CountryExp"]]: data[y][data_dict["GeoId"]]})
        elif data[y][data_dict["GeoId"]] != \
                data[y + 1][data_dict["GeoId"]] != data[y - 1][data_dict["GeoId"]]:
            country_number_dict.update({data[y][data_dict["CountryExp"]]: [z, y]})
    return country_list_number, country_number_dict, country_geold_dict


# create a list of the daily reports from a specific country (n = number of one the reports from this country)
def create_report_list(data_to_convert, report_number):
    print("  Extracting the data of {}...".format(data_to_convert[report_number][data_dict["CountryExp"]]))

    # extracting the data of one country using the latest report and comparing it to the other reports
    country_data = []
    for data_cell in data_to_convert:
        if data_cell[data_dict["CountryExp"]] == data_to_convert[report_number][data_dict["CountryExp"]]:
            country_data.append(data_cell)
    country_data.reverse()

    print("+ The data of {} has been successfully extracted !"
          .format(data_to_convert[report_number][data_dict["CountryExp"]]))
    return country_data


# convert data into lists of coords
def coordinates(country_data, date_raw_list):
    print("  Analysing the data to create the coordinates of the graph from {}...".format(country_name))

    # initializing variables
    pitch = 0
    i = 0
    country_new_conf_cases = []
    country_new_deaths = []

    # creating lists for the new confirmed cases and new deaths based on dates and removing missing data (nightmare)
    while i < len(date_raw_list):
        if i-pitch < len(country_data) and date_raw_list[i] == country_data[i-pitch][data_dict["DateRep"]]:
            country_new_conf_cases.append(int(country_data[i-pitch][data_dict["NewConfCases"]]))
            country_new_deaths.append(int(country_data[i-pitch][data_dict["NewDeaths"]]))
        else:
            country_new_conf_cases.append(0)
            country_new_deaths.append(0)
            pitch = pitch + 1
        i = i + 1

    # initializing other variables
    country_cumulative_new_conf_cases = []
    country_cumulative_new_deaths = []

    # creating the cumulative lists
    for i in range(len(country_new_conf_cases)):
        new_conf_cases_value = 0
        new_deaths_value = 0
        for j in range(i):
            new_conf_cases_value = new_conf_cases_value + country_new_conf_cases[j]
            new_deaths_value = new_deaths_value + country_new_deaths[j]
        country_cumulative_new_conf_cases.append(new_conf_cases_value)
        country_cumulative_new_deaths.append(new_deaths_value)

    print("+ Coordinates of the points from {} successfully created !".format(country_name))
    return country_cumulative_new_conf_cases, country_cumulative_new_deaths, country_new_conf_cases, country_new_deaths


# function that create a graph of a country using the data
def graph_country(country_data, y1, y2):
    print("  Attempting to create the graph of {}...".format(country_name))

    # draw the graph
    # check if country has enough cases and daily reports (you can change the value in constants)
    if max(y1) < cases_min:
        print("- Skipping {}, because the country has less than {:.0f} cases ({})\n"
              .format(country_data[0][data_dict["CountryExp"]], cases_min, max(y1)))
    elif len(date_full_list) < daily_report_min:
        print("- Skipping {}, because the country has less than {:.0f} daily reports ({:.0f})\n"
              .format(country_data[0][data_dict["CountryExp"]], daily_report_min, len(date_full_list)))
    # mat plot lib
    else:
        plt.rcParams.update({'font.size': 15})
        plt.figure(figsize=(12, 10))
        date_number_list = list(range(len(date_full_list)-1))
        plt.xlim(min(date_number_list), max(date_number_list)+1)
        plt.ylim(0, 1.2*max(y1))
        plt.plot(date_full_list, y1, color='#275b69', linestyle='solid', linewidth=4, label='Cumulative cases')
        plt.plot(date_full_list, y2, color='#913232', linestyle='solid', linewidth=4, label='Cumulative deaths')
        plt.axhline(y=max(y1), xmin=0, xmax=1, color='blue', alpha=0.5, linestyle=':', linewidth=1,
                    label='Total cases ({:.0f})'.format(max(y1)))
        plt.axhline(y=max(y2), xmin=0, xmax=1, color='red', alpha=0.5, linestyle=':', linewidth=1,
                    label='Total deaths ({:.0f})'.format(max(y2)))
        plt.fill_between(date_full_list, y1, y2, color='0.9')
        plt.fill_between(date_full_list, y2, 0, color='#c24e4e')

        if len(date_full_list) > 32:
            number_date_display = 2
        elif len(date_full_list) > 16:
            number_date_display = 2
        else:
            number_date_display = 1

        date_disp = [date_full_list[i] for i in range(len(date_full_list)) if (i % number_date_display) == 0]
        plt.gca().get_xaxis().set_ticklabels(date_disp, fontsize=10, rotation=60)
        plt.gca().get_xaxis().set_ticks([i for i in range(len(date_full_list)) if i % number_date_display == 0])

        plt.title("Graph of the evolution of the COVID in {}".format(country_name))
        plt.legend(loc='upper left')
        plt.xlabel('Date')
        plt.ylabel('Cases')
        filename = "{}.{}".format(country_name, graph_format)
        path = "{}{}".format(output_directory, filename)
        plt.savefig(path, dpi=None,
                    facecolor='w', edgecolor='w', papertype=None, format=graph_format, transparent=False,
                    bbox_inches=None, pad_inches=0.1)
        print("+ {} has been successfully proceed.\n".format(country_name))
        plt.close(path)
        total_cases = max(y1)
        return country_name, filename, total_cases


def write_html(figures):
    def create_image(country, filename):
        return """<img src="%s" alt="%s" class="col-lg-6 col-md-12"/>""" % (filename, country)

    with open("html/index.html", 'r') as file:
        template = file.read()
        images = []
        for country, filename, _ in figures[:display_top_n]:
            images.append(create_image(country, filename))
        result = template.replace("{0}", "\n".join(images))

        output_filename = "%s%s" % (output_directory, "index.html")
        with open(output_filename, "w") as output:
            output.write(result)


# constants (also used in the functions)
# exact name of the data file
name_file = "covid_data.xlsx"
# date of the first case (it will not change)
date_first_case = "31/12/2019"
# smallest number of cases or report to deal with the country
cases_min = 10
daily_report_min = 1
# output directory
output_directory = 'out/'
# format of the graph (png/pdf)
graph_format = "png"
graph_size = [12, 10]
# format of the data from different sources

data_dict_ecdc = \
    {"DateRep": 0, "NewConfCases": 4, "NewDeaths": 5, "CountryExp": 6, "GeoId": 7}
# https://www.ecdc.europa.eu/en/publications-data/download-todays-data-geographic-distribution-covid-19-cases-worldwide

# other sources coming soon

# format of the source you chose
data_dict = data_dict_ecdc

# number of images to display on html page
display_top_n = 16

# calling the functions
# calculated with the functions
data = xls_list(name_file)  # most important list
c_l_n, country_number_dict, country_geold = create_country_list()
date_full_list, date_raw_full_list = create_date_list()

# create output directory
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# country = data[country_list_number][data_dict["CountryExp"]]
# call the main functions

# create the graph to compare two country
"""
graph_two_country(
    create_report_list(data, int(country_number_dict["Italy"])),
    create_report_list(data, int(country_number_dict["Germany"])))

graph_two_country(
    create_report_list(data, int(country_number_dict["Italy"])),
    create_report_list(data, int(country_number_dict["France"])))
"""

# create the graph of all country

figures = []

for n in c_l_n:
    c_data = create_report_list(data, n)
    country_name = c_data[0][data_dict["CountryExp"]].replace("_", " ")  # new data base now use _
    c_c_new_conf_cases, c_c_new_deaths, c_new_conf_cases, c_new_deaths = coordinates(c_data, date_raw_full_list)
    result = graph_country(c_data, c_c_new_conf_cases, c_c_new_deaths)
    if result is not None:
        figures.append(result)

# sort images by descending order of cases
figures.sort(key=lambda t: -t[2])
# write html
write_html(figures)
