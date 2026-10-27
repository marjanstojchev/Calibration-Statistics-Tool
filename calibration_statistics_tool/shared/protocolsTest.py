import os #verzeichnise durchsuchen
import fnmatch # dateien filtern (suchmuster)
import io  #datei parsen
import operator


#testpathname = r'//fs9\MDSMS0/Kalibrierung/Kalibrierung_USM/Results/Typ_0x2CXXXX_UMRR-11'
#testpathname = r'\\fs9\MDSMS0\Kalibrierung\Kalibrierung_USM\Results\Typ_0x2CXXXX_UMRR-11\2018\intern_15xUMRR-110004-2C3800Jun2018'
#fileslisttemp = os.listdir(testpathname)  <- nur aktuelles verzeichnis

#for root, dirs, files in os.walk(testpathname):
#   for dir in dirs:
#        print('root: ' + root + ' dir: ' +dir)


class ProtocolInfoClass:
    def __init__(self):
        self.bFileEmpty      = False  # eol found empty protocol file
        self.bErrorOccured   = False # eol error found in protocol file
        self.bAbortCriterion = False # eol abbort criterion found in protocol file
        self.bLimitExceeded  = False  # eol abbort criterion found in protocol file
        self.PathName        = ''   # file path
        self.dateAndTime     = ''  # date and time
        self.productSerial   = ''# product serial number
        self.rf              = '' # rfboard number
        self.dsp             = '' # dsp board number




    # eventuell noch in extra file parse/filter klasse?
    # get filtered file list, filtered by matching search pattern
    @staticmethod
    def getfiltered_ptu2filelist(pathname, searchpattern):
        filteredfilescompletelist = []
        for root, dirs, files in os.walk(pathname):
            filteredlisttemp =  fnmatch.filter(files, searchpattern) #liste der passenden dateien im jeweiligen unterferzeichnis
            #print(filteredlisttemp)
            for filteredfile in filteredlisttemp: # fuege nun pfad + dateinamen zusammen fuer den kompletten dateipfad
                path = root + '/' + filteredfile
                filteredfilescompletelist.append(path)

        #print(filteredfilescompletelist)
        return filteredfilescompletelist

    # # eventuell noch in extra file parse/filter klasse?
    # # get filtered file list, filtered by matching search pattern
    @staticmethod
    def getfiltered_txantdiagramfilelist(pathname, protocolIdentifier):
        filteredfilescompletelist = []
        for root, dirs, files in os.walk(pathname):
            #for file in files:
                #print('root: ' + root + ' file: ' + file)
            for file in files:
                if fnmatch.fnmatch(file,'*'+ protocolIdentifier+'*') and fnmatch.fnmatch(file, '*TxAnt*') and fnmatch.fnmatch(file, '*Diagram*') and  fnmatch.fnmatch(file, '*.txt*') and not fnmatch.fnmatch(file.lower(), '*ptu2*') and not fnmatch.fnmatch(file, '*Protocol*'):
                    path=root +'/' + file
                    filteredfilescompletelist.append(path)
                # filteredlisttemp =  fnmatch.filter(files,searchpattern) #liste der passenden dateien im jeweiligen unterferzeichnis
                #print(filteredlisttemp)

            # for filteredfile in filteredlisttemp: # fuege nun pfad + dateinamen zusammen fuer den kompletten dateipfad
            #     filteredfilescompletelist.append(os.path.join(root, filteredfile))


        return filteredfilescompletelist

    # get all lines of this file as strings
    @staticmethod
    def getFileLines(fileNamePath):
        errorlisttemp = []
        content = []
        # Try to read the file
        try:
            f = io.open(fileNamePath, encoding='windows-1252', errors='ignore')

        # Catch an exception
        except IOError:
            # todo: den io error noch ausgeben in fehlerlist
            errorlisttemp.append('IO Error File with pathname '+ fileNamePath +  ' does not exist? / Insert a valid file path.')
        else:
            # Read the lines of the file and remove all white spaces
            with f:
                content = f.readlines()
            # strip erstmal and dieser stelle weglassen
            #content = [line.strip() for line in content] # leer zeichen am anfang und ende entfernen
        return content,errorlisttemp


    @staticmethod
    def getPreParseInfo(filelineslist):
        strEOLNoErrorString          = 'E=0;'
        strEOLNoAbortCriterionString = 'K=0;'
        strLimitExceeded             = 'M:'
        dateenum                     = 'Date:'
        timeenum                     = 'Time:'
        prodSerialenum               = 'Product-Serial:'
        rfenum                       = 'RF-Serial:'
        dspenum                      = 'Dsp-Serial:'
        # Initilizing variables
        date            = ''
        dateTime        = ''
        prodSerial      = ''
        rf              = ''
        dsp             = ''
        strHeader       = 'Measurment Durations:'
        bErrorOccured   = True
        bAbortCriterion = True
        bLimitExceeded  = False

        bFileEmpty = len(filelineslist) == 0
        if(bFileEmpty): # datei ist leer -> alle anderen werte auf false
            bErrorOccured = False
            bAbortCriterion = False
            bLimitExceeded = False
        
        for line in filelineslist:
            strTemp = line.strip() #alle leerzeichen am anfang und ende entfernen
            if strTemp.startswith(strHeader): # header zeile erreicht -> suche stoppen
                break
            strTemp = line.replace(' ','') #alle leerzeichen loeschen
            if strTemp.startswith(strEOLNoErrorString):
                bErrorOccured = False
            if strTemp.startswith(strEOLNoAbortCriterionString):
                bAbortCriterion = False
            if strTemp.startswith(strLimitExceeded): # achtung hier ist die suchlogik anders als bei error und abbruchkriterium ( nur wenn  'M:' gefunden wird -> dann ueberschreitung
                bLimitExceeded = True
            if strTemp.startswith(dateenum): # parse date
                linelist = strTemp.split(';')
                if len(linelist) > 1:
                    date = linelist[1].strip()
            if strTemp.startswith(timeenum): # parse time
                linelist = strTemp.split(';')
                if len(linelist) > 1:
                    dateTime = str(date) +'-' + str(linelist[1].strip())
            if strTemp.startswith(prodSerialenum): # parse product serial number
                linelist = strTemp.split(';')
                if len(linelist) > 1:
                    prodSerial = linelist[1].strip()
            if strTemp.startswith(rfenum): # parse rf number 
                linelist = strTemp.split(';')
                if len(linelist) > 1:
                    rf = linelist[1].strip()
            if strTemp.startswith(dspenum): # parse dsp number
                linelist = strTemp.split(';')
                if len(linelist) > 1:
                    dsp = linelist[1].strip()

        return bFileEmpty, bErrorOccured, bAbortCriterion, bLimitExceeded, dateTime, prodSerial, rf, dsp

    # alle protokolldatei im uebergebenen dateipfad und allen unterverzeichnissen
    @staticmethod
    def GetAllProtocolsList(pathname):
        return ProtocolInfoClass.getfiltered_ptu2filelist(pathname, '*[Pp]rotocol*.txt') # case-insensitive on Linux: matches Protocol and protocol


    # 'vorparsen' der protokolle: information ob fehler, abbruch kriterium oder messgrenzenueberschreitung aufgetreten ist
    @staticmethod
    def PreParseProtcols(protocolpathlist):
        ProtocolPreParseInfosList = []
        for protocolfilepath in protocolpathlist:
            linelist, errorlist = ProtocolInfoClass.getFileLines(protocolfilepath)
            if (len(errorlist) > 0):
                print(errorlist)  # noch durch logger ersetzen
            else:
                # pre parse nach error, abbruchkrit, limit ueberschritten
                # print('lines ' + str(len(linelist)) + ' in ' + protocolfilepath)
                cProtocolInfoTemp = ProtocolInfoClass()
                cProtocolInfoTemp.bFileEmpty, cProtocolInfoTemp.bErrorOccured, cProtocolInfoTemp.bAbortCriterion, cProtocolInfoTemp.bLimitExceeded, \
                    cProtocolInfoTemp.dateAndTime, cProtocolInfoTemp.productSerial, cProtocolInfoTemp.rf, cProtocolInfoTemp.dsp  = ProtocolInfoClass.getPreParseInfo(linelist)
                cProtocolInfoTemp.PathName = protocolfilepath
                ProtocolPreParseInfosList.append(cProtocolInfoTemp)

        bDebug = True
        if (bDebug):
            # print('found ' + str(len(ProtocolPreParseInfosList)) + ' protocols')
            emptyprotocolslist = []
            errorprotocolslist = []
            abbortcritprotocolslist = []
            LimitExceededprotocolslist = []
            for cProtcolPreInfo in ProtocolPreParseInfosList:
                if (cProtcolPreInfo.bFileEmpty):
                    emptyprotocolslist.append(cProtcolPreInfo.PathName)
                if (cProtcolPreInfo.bErrorOccured):
                    errorprotocolslist.append(cProtcolPreInfo.PathName)
                if (cProtcolPreInfo.bAbortCriterion):
                    abbortcritprotocolslist.append(cProtcolPreInfo.PathName)
                if (cProtcolPreInfo.bLimitExceeded):
                    LimitExceededprotocolslist.append(cProtcolPreInfo.PathName)
            # print('empty file in ' + str(len(emptyprotocolslist)) + ' of ' + str(len(ProtocolPreParseInfosList)))
            # print(emptyprotocolslist)
            # print('----------------')
            # print('errors in '+ str(len(errorprotocolslist))+ ' of ' + str(len(ProtocolPreParseInfosList)))
            # print(errorprotocolslist)
            # print('abbort criterions in '+ str(len(abbortcritprotocolslist))+ ' of ' + str(len(ProtocolPreParseInfosList)))
            # print(abbortcritprotocolslist)
            # print('----------------')
            # print('limits exceeded in '+ str(len(LimitExceededprotocolslist))+ ' of ' + str(len(ProtocolPreParseInfosList)))
            # print(abbortcritprotocolslist)
            # print('----------------')
        return ProtocolPreParseInfosList, emptyprotocolslist, errorprotocolslist, abbortcritprotocolslist, LimitExceededprotocolslist


    @staticmethod
    def FilterProtocols(ProtocolPreParseInfosList, bUseFilesWithError, bUseFilesAbbortCriterion, bUseFilesWIthLimitsExceeded):
        filteredProtocolsList    = []
        filteredOutProtocolsList = []

        for cProtocolPreParseInfo in ProtocolPreParseInfosList:

            # # wenn keine der ausschluss bedingungen zutrifft -> datei zur 'akzeptiert' list hinzu
            if not (((not bUseFilesWithError) and cProtocolPreParseInfo.bErrorOccured)
                    or ((not bUseFilesAbbortCriterion) and cProtocolPreParseInfo.bAbortCriterion)
                    or ((not bUseFilesWIthLimitsExceeded) and cProtocolPreParseInfo.bLimitExceeded)):
                if not cProtocolPreParseInfo.bFileEmpty:
                    filteredProtocolsList.append(cProtocolPreParseInfo)
            else:
                filteredOutProtocolsList.append(cProtocolPreParseInfo)


        # Sort the list base on date and DSP number
        filteredProtocolsList = sorted(filteredProtocolsList, key=operator.attrgetter('dateAndTime'))
        filteredProtocolsList = sorted(filteredProtocolsList, key=operator.attrgetter('dsp'))
        filteredOutProtocolsList = sorted(filteredOutProtocolsList, key=operator.attrgetter('dateAndTime'))
        filteredOutProtocolsList = sorted(filteredOutProtocolsList, key=operator.attrgetter('dsp'))
        # return the list
        return filteredProtocolsList, filteredOutProtocolsList

    @staticmethod
    def FilterNewProtocols(acceptedProtocolsList):
        filteredNewList = []
        # Sort the list base on date and DSP number
        # acceptedProtocolsList = sorted(acceptedProtocolsList, key=operator.attrgetter('dateAndTime'))
        # acceptedProtocolsList = sorted(acceptedProtocolsList, key=operator.attrgetter('dsp'))
        # sorting
        for idx in range(1, len(acceptedProtocolsList)):
            # Compare serial number
            if acceptedProtocolsList[idx-1].productSerial == acceptedProtocolsList[idx].productSerial:
                # Compare rf and dsp board 
                if acceptedProtocolsList[idx-1].dsp == acceptedProtocolsList[idx].dsp and \
                    acceptedProtocolsList[idx-1].rf == acceptedProtocolsList[idx].rf:
                        # Compare date and time
                        date1 = acceptedProtocolsList[idx-1].dateAndTime
                        date2 = acceptedProtocolsList[idx].dateAndTime
                        if date1 > date2:
                            filteredNewList.append(acceptedProtocolsList[idx-1])
                        else:
                            if idx == len(acceptedProtocolsList)-1:
                                filteredNewList.append(acceptedProtocolsList[idx])
                else:
                    filteredNewList.append(acceptedProtocolsList[idx-1])
                    if idx == len(acceptedProtocolsList)-1:
                        filteredNewList.append(acceptedProtocolsList[idx])
            else:
                filteredNewList.append(acceptedProtocolsList[idx-1])
                if idx == len(acceptedProtocolsList)-1:
                    filteredNewList.append(acceptedProtocolsList[idx])
        
        # If there is only one protocol just use that protocol
        if len(filteredNewList) == 0:
            filteredNewList = acceptedProtocolsList
            
        return filteredNewList

#print('empty file in ' + str(len(emptyprotocolslist)) + ' of ' + str(len(protocolslist)))
#print(emptyprotocolslist)
#print('----------------')
#print('errors in '+ str(len(errorprotocolslist))+ ' of ' + str(len(protocolslist)))
#print(errorprotocolslist)
#print('abbort criterions in '+ str(len(abbortcritprotocolslist))+ ' of ' + str(len(protocolslist)))
#print(abbortcritprotocolslist)
#print('----------------')
#print('limits exceeded in '+ str(len(LimitExceededprotocolslist))+ ' of ' + str(len(protocolslist)))
#print(abbortcritprotocolslist)
#print('----------------')
#print('EOL Ok in '+ str(len(Okprotocolslist))+ ' of ' + str(len(protocolslist)))
#print(Okprotocolslist)
#print('----------------')
#print('end')
#return Okprotocolslist

