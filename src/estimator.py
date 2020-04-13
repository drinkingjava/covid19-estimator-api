import json
import logging

sample_data = {
    'region': {
        'name': 'Africa',
        'avgAge': 19.7,
        'avgDailyIncomeInUSD': 4,
        'avgDailyIncomePopulation': 0.73
    },
    'periodType': 'days',
    'timeToElapse': 38,
    'reportedCases': 2747,
    'population': 92931687,
    'totalHospitalBeds': 678874
}

stats = {
    'region': {
        'name': 'Africa',
        'avgAge': 19.7,
        'avgDailyIncomeInUSD': 5,
        'avgDailyIncomePopulation': 0.71
    },
    'periodType': 'days',
    'timeToElapse': 58,
    'reportedCases': 674,
    'population': 66622705,
    'totalHospitalBeds': 1380614
}


def requestedTimeFactorCalculator(periodType, timeToElapse):
    if periodType == 'days':
        days = timeToElapse
        logging.debug(
            'using {} days'.format(days))
        return 2 ** int(days/3)
    elif periodType == 'weeks':
        days = timeToElapse * 7
        logging.debug(
            'using {} weeks which has {} days'.format(timeToElapse, days))
        return 2 ** int(days/3)
    elif periodType == 'months':
        days = timeToElapse * 30
        logging.debug(
            'using {} months which has {} days'.format(timeToElapse, days))
        return 2 ** int(days/3)
    else:
        raise Exception(
            'Period should be days, weeks or months'
            '{} was given'.format(periodType))


def timeToElapseInDays(periodType, timeToElapse):
    if periodType == 'days':
        days = timeToElapse
        logging.debug(
            'using {} days'.format(days))
        return days
    elif periodType == 'weeks':
        days = timeToElapse * 7
        logging.debug(
            'using {} weeks which has {} days'.format(timeToElapse, days))
        return days
    elif periodType == 'months':
        days = timeToElapse * 30
        logging.debug(
            'using {} months which has {} days'.format(timeToElapse, days))
        return days
    else:
        raise Exception(
            'Period should be days, weeks or months'
            '{} was given'.format(periodType))


def bedAvailabilityCalculator(totalHospitalBeds, severeCasesByRequestedTime):
    occupied = totalHospitalBeds * 0.65
    available = totalHospitalBeds - occupied
    availableForPatients = available - severeCasesByRequestedTime
    return int(availableForPatients)


def dollarsInFlightCalculator(infectionsByTime, avgIncomePop, avgIncome,
                              periodType, period):
    days = timeToElapseInDays(periodType, period)
    return int((infectionsByTime * avgIncomePop * avgIncome) / days)


def impact(data, impactType):
    reportedCases = data['reportedCases']
    if impactType == 'normal':
        currentlyInfected = reportedCases * 10
    elif impactType == 'severe':
        currentlyInfected = reportedCases * 50
    else:
        raise Exception('Unsupported impact type given')

    totalBeds = data['totalHospitalBeds']
    timeToElapse = data['timeToElapse']
    periodType = data['periodType']
    timeFactor = requestedTimeFactorCalculator(
        periodType, timeToElapse)
    avgIncome = data['region']['avgDailyIncomeInUSD']
    avgIncomePop = data['region']['avgDailyIncomePopulation']
    infectionsByRequestedTime = currentlyInfected * timeFactor
    severeCasesByRequestedTime = int(infectionsByRequestedTime * 0.15)
    hospitalBedsByRequestedTime = bedAvailabilityCalculator(
        totalBeds, severeCasesByRequestedTime)
    casesForICUByRequestedTime = int(infectionsByRequestedTime * 0.05)
    casesForVentilators = int(infectionsByRequestedTime * 0.02)
    dollarsInFlight = dollarsInFlightCalculator(infectionsByRequestedTime,
                                                avgIncomePop, avgIncome,
                                                periodType, timeToElapse)
    return dict(currentlyInfected=currentlyInfected,
                infectionsByRequestedTime=infectionsByRequestedTime,
                severeCasesByRequestedTime=severeCasesByRequestedTime,
                hospitalBedsByRequestedTime=hospitalBedsByRequestedTime,
                casesForICUByRequestedTime=casesForICUByRequestedTime,
                casesForVentilatorsByRequestedTime=casesForVentilators,
                dollarsInFlight=dollarsInFlight)


def estimator(data):
    data = {
        'data': data,
        'impact': impact(data, 'normal'),
        'severeImpact': impact(data, 'severe')
    }
    return data
