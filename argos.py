import httplib
import re
import xml.dom.minidom
import xml.etree.ElementTree as ET


ARGOS_HOST = "ws-argos.clsamerica.com"


def argosRequest(request):
    conn = httplib.HTTPConnection(ARGOS_HOST)
    conn.request("POST", "/argosDws/services/DixService", request)
    response = conn.getresponse()
    #print response.status, response.reason, response.msg
    data = response.read()
    #print data
    conn.close()
    return data

def cleanupXml(data):
    body = re.search("<return>(.*)</return>", data, flags=re.S)
    if (body):
        body = body.group(1)
        body = re.sub("&lt;", "<", body)
        body = re.sub("&gt;", ">", body)
        body = re.sub("&amp;", "&", body)
        ugly_xml = xml.dom.minidom.parseString(body)
        ugly_xml = ugly_xml.toprettyxml(indent='  ')
        text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)    
        pretty_xml = text_re.sub('>\g<1></', ugly_xml)
        return pretty_xml

def cleanupCsv(data):
    body = re.search("<return>(.*)</return>", data, flags=re.S)
    if (body):
        body = body.group(1)
        return body


def getPlatforms(username, password, programNumber):
    argosXml = getXml(username, password, programNumber, type="program", nbPassByPtt=1)
    root = ET.fromstring(argosXml)
    platformIds = []
    for platform in root.findall(".//platform"):
        #ET.dump(platform)
        platformIds.append(int(platform.find("platformId").text))
    return platformIds



def getCsv(username, password, id, type="platform", nbPassByPtt=10, nbDaysFromNow=10, mostRecentPassages="true", displaySensor="false"):
    if (type == "program"):
        type = "<typ:programNumber>" + str(id) + "</typ:programNumber>"
    else:
        type = "<typ:platformId>" + str(id) + "</typ:platformId>"

    request = (
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:typ="http://service.dataxmldistribution.argos.cls.fr/types">\n'
        '<soap:Header/>\n'
        '<soap:Body>\n'
        '<typ:csvRequest>\n'
        '<typ:username>%s</typ:username>\n'
        '<typ:password>%s</typ:password>\n'
        '%s\n'
        '<typ:nbPassByPtt>%d</typ:nbPassByPtt>\n'
        '<typ:nbDaysFromNow>%d</typ:nbDaysFromNow>\n'
        '<typ:mostRecentPassages>%s</typ:mostRecentPassages>\n'
        '<typ:displayLocation>true</typ:displayLocation>\n'
        '<typ:displayRawData>false</typ:displayRawData>\n'
        '<typ:displaySensor>%s</typ:displaySensor>\n'
        '<typ:showHeader>true</typ:showHeader>\n'
        '</typ:csvRequest>\n'
        '</soap:Body>\n'
        '</soap:Envelope>'
        ) % (username, password, type, nbPassByPtt, nbDaysFromNow, mostRecentPassages, displaySensor)


    #print request
    data = argosRequest(request)
    data = cleanupCsv(data)
    return data


def getKml(username, password, id, type="platform", nbPassByPtt=10, nbDaysFromNow=10, mostRecentPassages="true"):
    if (type == "program"):
        type = "<typ:programNumber>" + str(id) + "</typ:programNumber>"
    else:
        type = "<typ:platformId>" + str(id) + "</typ:platformId>"

    request = (
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:typ="http://service.dataxmldistribution.argos.cls.fr/types">\n'
        '<soap:Header/>\n'
        '<soap:Body>\n'
        '<typ:kmlRequest>\n'
        '<typ:username>%s</typ:username>\n'
        '<typ:password>%s</typ:password>\n'
        '%s\n'
        '<typ:nbPassByPtt>%d</typ:nbPassByPtt>\n'
        '<typ:nbDaysFromNow>%d</typ:nbDaysFromNow>\n'
        '<typ:mostRecentPassages>%s</typ:mostRecentPassages>\n'
        '<typ:displayDescription>true</typ:displayDescription>\n'
        '</typ:kmlRequest>\n'
        '</soap:Body>\n'
        '</soap:Envelope>'
        ) % (username, password, type, nbPassByPtt, nbDaysFromNow, mostRecentPassages)


    #print request
    data = argosRequest(request)
    data = cleanupXml(data)
    return data


def getXml(username, password, id, type="platform", nbPassByPtt=10, nbDaysFromNow=10, mostRecentPassages="true", displaySensor="false"):
    if (type == "program"):
        type = "<typ:programNumber>" + str(id) + "</typ:programNumber>"
    else:
        type = "<typ:platformId>" + str(id) + "</typ:platformId>"

    request = (
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:typ="http://service.dataxmldistribution.argos.cls.fr/types">\n'
        '<soap:Header/>\n'
        '<soap:Body>\n'
        '<typ:xmlRequest>\n'
        '<typ:username>%s</typ:username>\n'
        '<typ:password>%s</typ:password>\n'
        '%s\n'
        '<typ:nbPassByPtt>%d</typ:nbPassByPtt>\n'
        '<typ:nbDaysFromNow>%d</typ:nbDaysFromNow>\n'
        '<typ:mostRecentPassages>%s</typ:mostRecentPassages>\n'
        '<typ:displayLocation>true</typ:displayLocation>\n'
        '<typ:displayRawData>false</typ:displayRawData>\n'
        '<typ:displaySensor>%s</typ:displaySensor>\n'
        '</typ:xmlRequest>\n'
        '</soap:Body>\n'
        '</soap:Envelope>'
        ) % (username, password, type, nbPassByPtt, nbDaysFromNow, mostRecentPassages, displaySensor)


    #print request
    data = argosRequest(request)
    data = cleanupXml(data)
    return data



def getLocations(argos_xml):
    root = ET.fromstring(argos_xml)
    locations = []
    for location in root.findall(".//location"):
        #ET.dump(location)
        location_date = location.find("locationDate").text
        latitude = float(location.find("latitude").text)
        longitude = float(location.find("longitude").text)
        current_location = [location_date, latitude, longitude]
        locations.append(current_location)

    if (len(locations) == 0):
        return None
    else:
        return locations



def get_current_location(username, password, platform_id):
    argos_xml = getXml(username, password, platform_id)
    locations = getLocations(argos_xml)
    current_loc = sorted(locations).pop()
    return current_loc


# new stuff


