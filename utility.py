month_dict = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

def convertDate(date):
    dateList = date.split('-')
    res = month_dict[dateList[1]] + '/'
    if len(dateList[0]) == 1:
        res += '0' + dateList[0] + '/'
    else:
        res += dateList[0] + '/'
    if int(dateList[2]) > 17:
        res += '19' + dateList[2]
    else:
        res += '20' + dateList[2]
    return res

