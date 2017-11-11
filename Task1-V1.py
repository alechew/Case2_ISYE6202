import Classes
import numpy
import random
import statistics

filename = ""

yearName = ["2018-1", "2018-2", "2018-3", "2018-4", "2018-5"]
dayName = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

factorySpecifications = Classes.FactorySpecificationsTask2
leadTimes = [15, 7, 5, 2, 1]

demandDistribution = Classes.DemandVar(100000000, 10000000)
yearlyDemand = []     # this can be said is the mean of every new year demand
yearlyStandardDeviation = []    # this can be said is the standardDeviation of every new year demand
dailyCapacityRequirements = []

totalDaysInYear = 365
years = 5
months = 12
days = 7

monthlyDemand = []
monthlyDemandAverage = [0.11, 0.06, 0.08, 0.10, 0.08, 0.07, 0.11, 0.09, 0.08, 0.08, 0.07, 0.07]
monthlyDemandStandardDeviation = [0.0268, 0.0161, 0.0195, 0.0249, 0.0206, 0.0180, 0.0285, 0.0216,
                                  0.0197, 0.0195, 0.0176, 0.0172]

monthInYear = [Classes.MonthInfo(31, 0), Classes.MonthInfo(28, 3), Classes.MonthInfo(31, 3), Classes.MonthInfo(30, 6),
               Classes.MonthInfo(31, 1), Classes.MonthInfo(30, 4), Classes.MonthInfo(31, 6), Classes.MonthInfo(31, 2),
               Classes.MonthInfo(30, 5), Classes.MonthInfo(31, 0), Classes.MonthInfo(30, 3), Classes.MonthInfo(31, 5)]


dailyDemand = []
dailyDemandStandardDeviation = []
# daily Factors
pConstraints = [0.714, 0.221, 0.217, 0.461, 0.768, 0.580, 0.373]
triangularMin = [0.08, 0.08, 0.11, 0.14, 0.12, 0.10, 0.13]
triangularAvg = [0.13, 0.10, 0.13, 0.17, 0.17, 0.16, 0.15]
triangularMax = [0.15, 0.17, 0.20, 0.21, 0.19, 0.20, 0.17]


# this contain the demand of everyday for every year as a single list. This gets later divided into their respective
# years.
dailyDemandList = []

# this is the mean and deviation of the generated daily random demands.
yearMeanOfRandomDemand = []
yearDeviationOfRandomDemand = []

# will have 5 list with the demand for every year iteration
eachYearDailyDemandList = []


def write_to_file():
    """writes on a CSV value the randomly generated daily demands from year 2018 to 2023
    """
    ofile = open(filename + "_Generated-Random-Demand-Originating Sample City.csv", "wb")

    # writing the title of the columns
    row = "Year,Month,Day,Demand\n"
    ofile.write(row)

    for j in range(0, len(eachYearDailyDemandList),1):
        theYearDemand = eachYearDailyDemandList[j]

        for i in range(0, len(theYearDemand), 1):
            day = theYearDemand[i]
            if isinstance(day, Classes.DailyDemand):
                row = day.year + "," + day.week + "," + day.day + "," + str(day.dailyDemand) + "\n"
            ofile.write(row)
        ofile.write("\n")
    ofile.close()


def generate_beta_monthly(index):
    """generates weekly demand ratio following normal distribution with
     mean and standard deviation for its respective year"""

    return numpy.random.normal(monthlyDemandAverage[index], monthlyDemandStandardDeviation[index])


def generate_raw(index):
    """randomly generates daily demand ratio following triangular distribution"""
    p = random.uniform(0, 1)
    raw = 0
    if p <= pConstraints[index]:
        raw = triangularMin[index] \
              + numpy.math.sqrt(p * (triangularMax[index] - triangularMin[index]) * (triangularAvg[index] - triangularMin[index]))
    else:
        raw = triangularMax[index] \
              - numpy.math.sqrt((1 - p) * (triangularMax[index] - triangularMin[index]) * (triangularMax[index] - triangularAvg[index]))
    return raw


# I think this is where all starts

# Generate yearly random demands;
count = 0
while count <= years:
    demand = demandDistribution.generate_random_demand()
    yearlyDemand.append(demand)
    count = count + 1



# here we calculate the daily demand
for x in range(years):
    if x > 0:
        eachYearDailyDemandList.append(dailyDemandList)

    dailyDemandList = []
    for i in range(months):
        beta = generate_beta_monthly(i)
        monthDemand = beta * yearlyDemand[x]
        monthlyDemand.append(monthDemand)

        rangeOfDaysInMonth = monthInYear[i].totalDays
        firstDay = monthInYear[i].firstDayNumberinWeek
        j = firstDay
        totalIterations = firstDay + rangeOfDaysInMonth

        while j < totalIterations:
            dayOfWeek = j % 7

            raw = generate_raw(dayOfWeek)

            singleDayDemand = round(monthlyDemand[i] * raw, 0)
            dailyDemand = Classes.DailyDemand(yearName[x], str(i + 1), dayName[dayOfWeek], yearlyDemand[x], monthlyDemand[i]
                                              , singleDayDemand, x, i, dayOfWeek)
            dailyDemandList.append(dailyDemand)
            j = j + 1



# outputs in console the daily demand generated for each year
count = 1
for day in dailyDemandList:
    if isinstance(day, Classes.DailyDemand):
        print("Year: " + day.year + ", " + day.week + ", " + day.day + ", " + str(day.dailyDemand))
        if count % 365 == 0:
            print("\n")
    count += 1

write_to_file()


