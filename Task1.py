import Classes
import numpy
import random
import statistics

"""
    calculates the Estimate 2018 - 2023 demand satisfaction capacity requirements according to task2 Assumptions
    promising 15, 7, 5, 2 or 1 day-s for order-to-shipping time and service levels of 99%, 99.5% vs. 99.9%.
"""

filename = ""

yearName = ["2018-1", "2018-2", "2018-3", "2018-3", "2018-4", "2018-5"]
yearsOfGrowth = 5
dayName = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

factorySpecifications = Classes.FactorySpecificationsTask2
leadTimes = [15, 7, 5, 2, 1]

demandDistribution = Classes.DemandVar(100000000, 10000000)
yearlyDemand = []     # this can be said is the mean of every new year demand
yearlyStandardDeviation = []    # this can be said is the standardDeviation of every new year demand
dailyCapacityRequirements = []

totalDaysInYear = 364
years = 6
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


def write_to_file():
    """writes on a CSV value the randomly generated daily demands from year 2018 to 2023
    """
    ofile = open(filename + "_Generated-Random-Demand.csv", "wb")

    # writing the title of the columns
    row = "Year,Week,Day,Demand\n"
    ofile.write(row)

    for i in range(0, len(dailyDemandList), 1):
        day = dailyDemandList[i]
        if isinstance(day, Classes.DailyDemand):
            row = day.year + "," + day.week + "," + day.day + "," + str(day.dailyDemand) + "\n"
        ofile.write(row)
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


def calculate_mean_deviation():
    """calculating mean and standard deviation for the total of the random generated daily demand for each yearly demand."""

    for i in range(6):
        yearList = eachYearDailyDemandList[i]
        demand = []
        for j in range(len(yearList)):
            obj = yearList[j]
            if isinstance(obj, Classes.DailyDemand):
                demand.append(obj.dailyDemand)

        theStdDeviation = statistics.stdev(demand)
        theMean = statistics.mean(demand)
        yearMeanOfRandomDemand.append(theMean)
        yearDeviationOfRandomDemand.append(theStdDeviation)


def calculate_daily_capacity_v2():
    """Calculates the daily capacity required to fullfill yearly demand based on OTS and Service level."""

    global filename
    leadTime = input("Enter Lead Time")
    serviceLevel = input("Enter Service Level")
    filename = "Lead_Time_" + str(leadTime) + "_Service_Level_" + str(serviceLevel)

    factorySpecifications = Classes.FactorySpecificationsTask2(leadTimes, yearMeanOfRandomDemand,
                                                             yearDeviationOfRandomDemand, serviceLevel, leadTime)

    factorySpecifications.set_lead_time(leadTime)

    for x in range(len(factorySpecifications.yearlyDemandRequirements)):
        leftSide = (factorySpecifications.yearlyDemandRequirements[x] * factorySpecifications.leadTime)
        valueInsideSqrt = pow(factorySpecifications.yearlyStandardDeviations[x], 2) * factorySpecifications.leadTime
        dailyCapacity = (leftSide + factorySpecifications.zNormalValue * numpy.sqrt(valueInsideSqrt)) / factorySpecifications.leadTime

        dailyCapacityRequirements.append(int(dailyCapacity))
    factorySpecifications.dailyCapacity = dailyCapacityRequirements
    return factorySpecifications


# I think this is where all starts

# Generate yearly random demands;
count = 0
while count <= years:
    demand = demandDistribution.generate_random_demand()
    yearlyDemand.append(demand)
    count = count + 1

# here we calculate the daily demand
for x in range(years):
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


index = 0
eachYearDailyDemandList = []
totalYears = len(dailyDemandList) / totalDaysInYear
tempList = []

# separating each year.
for x in range(totalYears):
    tempList = [dailyDemandList[index]]
    index += 1
    while index % 364 != 0:
        tempList.append(dailyDemandList[index])
        index += 1
    eachYearDailyDemandList.append(tempList)


# calculating standard deviation for the random data generated.
calculate_mean_deviation()

# generates the daily capacity requirements for each lead time and service level.
# factorySpecifications = calculate_daily_capacity_v2()


# outputs in console the daily demand generated for each year
count = 1
for day in dailyDemandList:
    if isinstance(day, Classes.DailyDemand):
        print("Year: " + day.year + ", " + day.week + ", " + day.day + ", " + str(day.dailyDemand))
        if count % 364 == 0:
            print("\n")
    count += 1

write_to_file()


# calculates the year demands daily demand and amount shipped and calculates the average of service satisfaction level.
def summarize_year_demands():
    for x in range(totalYears):
        totalDemand = 0
        totalProduced = 0
        totalCapacity = 0
        totalShipped = 0
        for obj in yearTotalDemand[x]:
            if isinstance(obj, Classes.DayManufactured):
                totalDemand += obj.demand
                totalProduced += obj.produced
                totalCapacity += factorySpecifications.dailyCapacity[factorySpecifications.scenario]
                totalShipped += obj.amountShipped

        satisfaction = totalShipped / float(totalDemand)
        currentYearSummary = Classes.YearSummary(totalDemand, totalCapacity, totalProduced, totalShipped,
                                                 satisfaction)
        yearSummarizeOverPeriod.append(currentYearSummary)


def write_yearly_summary():
    """writes into a CSV File the average of the daily demand fulfilled service level for each year"""

    file_name = filename + "_Yearly-Summary.csv"
    ofile = open(file_name, "wb")

    # writing the title of the columns
    row = "Year, Total Demand, Total Shipped, Satisfaction Level\n"
    ofile.write(row)

    count = 1
    for x in yearSummarizeOverPeriod:

        if isinstance(x, Classes.YearSummary):
            row = str(count) + "," + str(x.yearDemand) + "," + str(x.totalShipped) + "," \
                  + str(round(x.satisfactionLevel, 6)) + "\n"
            ofile.write(row)
        count = count + 1

    row = "Lead Time, Satisfaction Level\n"
    ofile.write(row)
    row = str(factorySpecifications.leadTime) + "," + str(factorySpecifications.serviceTargetLevel)
    ofile.write(row)
    ofile.close()




"""


# Calculates the daily satisfaction level based on randomly generated demand.
yearTotalDemand = []
yearSummarizeOverPeriod = []
currentYearIndex = 0
for i in range(totalYears):

    listOfDaysProducing = []
    totalDemandInOneDay = 0
    totalDemandFulfilledInOneYear = 0
    totalLoss = 0
    backlog = 0  # very important variable as this temporarily store the missing parts produced previous day.

    dailyManufacturingCapacity = factorySpecifications.dailyCapacity[currentYearIndex]

    yearList = eachYearDailyDemandList[i]

    for k in range(len(yearList)):
        dayDemandGenerated = yearList[k]
        if isinstance(dayDemandGenerated, Classes.DailyDemand):
            generatedDailyDemand = dayDemandGenerated.dailyDemand

            if factorySpecifications.leadTime > 1:
                if k < factorySpecifications.leadTime - 1:
                    ordersToShipToday = round(dayDemandGenerated.weeklyDemand * generate_raw(dayDemandGenerated.dayNumber), 0)
                else:
                    if factorySpecifications.leadTime != 1 and k != 0:
                        index = int(k - (factorySpecifications.leadTime - 1))
                        ordersToShipToday = listOfDaysProducing[
                            index].demand  # of the item on the list of all saved dayManufactored
            else:
                ordersToShipToday = round(dayDemandGenerated.weeklyDemand * generate_raw(dayDemandGenerated.dayNumber), 0)

            if k == 0:
                backlog = 0
                prevDayInventory = min(generatedDailyDemand, dailyManufacturingCapacity)
                prevDayAmountShipped = round(dayDemandGenerated.weeklyDemand * generate_raw(dayDemandGenerated.dayNumber), 0)
            else:
                if isinstance(listOfDaysProducing[k - 1], Classes.DayManufactured):
                    prevDayInventory = listOfDaysProducing[k - 1].inventory
                    backlog = listOfDaysProducing[k - 1].thisDayBackLog

            dayManufactured = Classes.DayManufactured(backlog, generatedDailyDemand, prevDayInventory, ordersToShipToday)

            if dayManufactured.needToProduce > dailyManufacturingCapacity:
                dayManufactured.thisDayBackLog = dayManufactured.needToProduce - dailyManufacturingCapacity  # Calculating backlog
            else:
                dayManufactured.thisDayBackLog = 0

            dayManufactured.produced = min(dayManufactured.needToProduce, dailyManufacturingCapacity)

            if k == 0:
                dayManufactured.amountShipped = min(dayManufactured.ordersToShip, dayManufactured.inventory)
                dayManufactured.satisfactionPercentage = 1.0
                if dayManufactured.ordersToShip > dayManufactured.inventory:
                    dayManufactured.inventory = 0
                else:
                    dayManufactured.inventory = dayManufactured.needToProduce - dayManufactured.ordersToShip
            else:
                dayManufactured.inventory = dayManufactured.inventory + dayManufactured.produced
                dayManufactured.amountShipped = min(dayManufactured.inventory, dayManufactured.ordersToShip)
                if dayManufactured.inventory < dayManufactured.ordersToShip:
                    dayManufactured.demandUnfilled = dayManufactured.ordersToShip - (
                    dayManufactured.inventory + dayManufactured.produced)
                    dayManufactured.inventory = 0
                else:
                    dayManufactured.inventory = dayManufactured.inventory - dayManufactured.ordersToShip

                if dayManufactured.amountShipped == dayManufactured.ordersToShip:
                    dayManufactured.satisfactionPercentage = 1.0
                else:
                    dayManufactured.satisfactionPercentage = (
                    dayManufactured.amountShipped / float(dayManufactured.ordersToShip))

            listOfDaysProducing.append(dayManufactured)
    currentYearIndex += 1
    yearTotalDemand.append(listOfDaysProducing)
"""

summarize_year_demands()
write_yearly_summary()
