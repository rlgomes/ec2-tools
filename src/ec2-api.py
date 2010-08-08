#!/usr/bin/python
'''
Created on Apr 26, 2010

@author: Rodney Gomes <rodneygomes@gmail.com>

@summary: simple utility to generate the correct HTTP url to hit when trying
to execute one of the many web service calls available for the ec2 API.

'''
import httplib
import urllib
import hmac
import base64
import hashlib
import sys
import getopt

from datetime import date

def usage():
    print "ec2-api.py --host=host --secret=secret --key=key [-x --extra=args --method=GET] [action]"
    print "options:" 
    print "         -x             -> execute the request."
    print "         -method=method -> defaults to GET."
    print "         -extra=args    -> extra arguments to attach to the ec2 operation,"
    print "         -host=host     -> extra arguments to attach to the ec2 operation,"
    print "                           in the format a=b&c=d&etc"
    print "         -key=key       -> aws key id"
    print "         -secret=secret -> aws secret key"

try:
    opts, args = getopt.getopt(sys.argv[1:], "hx", [
                                                    "host=",
                                                    "key=",
                                                    "secret=",
                                                    "extra=",
                                                    "method="
                                                   ])
except getopt.GetoptError, err:
    print str(err) 
    usage()
    sys.exit(2)

eargs   = ""
method  = "GET"
execute = False

for (o, v) in opts:
    if o == "-h":
        usage()
        sys.exit(0)
    elif o == "-x":
        execute = True
    elif o == "--extra":
        eargs = v
    elif o == "--host":
        host = v
    elif o == "--key":
        awskey = v 
    elif o == "--secret":
        awssec = v 
    elif o == "--method":
        method = v 

url="/"
action=args[0]

params = { 'Action' : action,
           'AWSAccessKeyId' : awskey,
           'Timestamp' : '2011-01-01',
           'Version': '2010-06-15',
           'SignatureMethod' : 'HmacSHA256',
           'SignatureVersion' : '2' }

if eargs != "":
    extra_args = eargs.split("&")
    for arg in extra_args:
	    splitup = arg.split("=")
	    key = splitup[0]
	    val = splitup[1]
	    params[key] = val

signature = "%s\n%s\n%s\n" % (method,host,url)

encoded_params=""
for key in sorted(params.iterkeys()):
    ekey = urllib.quote(key)
    evalue = urllib.quote(params[key])
    encoded_params = "%s&%s=%s" % (encoded_params, ekey, evalue)
   
encoded_params = encoded_params[1:]

signature = "%s%s" % (signature,encoded_params)

h = hmac.new(awssec, signature, hashlib.sha256)
signature = h.digest()
signature = base64.b64encode(signature)
signature = urllib.quote(signature)

eparams=""
for key in sorted(params.iterkeys()):
    ekey = urllib.quote(key)
    evalue = urllib.quote(params[key])
    eparams = "%s&%s=%s" % (eparams, ekey, evalue)
   
eparams = "%s&Signature=%s" % (eparams[1:],signature)

url = "https://%s/?%s" % (host,eparams)
print "%s %s" % (method,url)

if execute:
	f = urllib.urlopen(url)
	print f.read()


