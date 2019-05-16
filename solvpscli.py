#!/usr/bin/env python3
import robobrowser
from urllib.parse import urlparse, parse_qsl, urljoin, urlencode, quote
import webbrowser
import argparse
from getpass import getpass
import os
from json import loads

actions = ('status','browse','boot','reboot','shutdown','ssh','passwd')
p = argparse.ArgumentParser(description='''
This is a tool to manage SolVPS virtual private servers directly from the command line.

It works by scraping the web-based user interface at https://www.solvps.com/secure/clientarea.php
''')
p.add_argument('vpsid', nargs='?', help="SolVPS numeric ID, or domain name")
p.add_argument('action', nargs='?', default='status', choices=actions,
               help="Action to perform on the VPS (ssh to console is only available for Linux systems)")
p.add_argument('--show-passwords', action='store_true',
               help="Show password fields in status output")
p.add_argument('-u','--username')
p.add_argument('-p','--password')
args = p.parse_args()

username = args.username
password = args.password
if not (username or password):
    try:
        username, password = (l.strip() for l in open(os.path.expanduser('~/.solvps_credentials')))
    except (IOError, ValueError):
        print("Could not read SolVPS credentials from ~/.solvps_credentials")
        print("File should contain username on the line #1, password on line #2.")
if not username:
    username = input("SolVPS username: ")
if not password:
    password = getpass("SolVPS password: ")

########################################

print("Logging in to SolVPS...")
br=robobrowser.RoboBrowser(parser='html.parser', user_agent='solvpscli')
br.open( 'https://www.solvps.com/secure/dologin.php?%s' % urlencode((('username',username),('password',password))) )
if 'incorrect=true' in br.url:
    p.error('Incorrect username or password')

########################################

# Identify numeric ID of VPS and management URL, or list possibilities, by parsing HTML that
# looks like this:
#
#   <a menuItemName="0" href="/secure/clientarea.php?action=productdetails&id=12345" class="list-group-item" id="ClientAreaHomePagePanels-Active_Products_Services-0">
#   Windows VPS - Custom Windows VPS<br /><span class="text-domain">xyzdomain.company.com</span></a>

if args.vpsid and args.vpsid.isdigit():
    vps_id = int(args.vpsid)
    url = 'https://www.solvps.com/secure/clientarea.php?action=productdetails&id=%d' % vps_id

else:
    spans = br.find_all("span", {'class':'text-domain'})
    try:
        parsed = [(span.text, span.parent['href'],
                   int(dict(parse_qsl(urlparse(span.parent['href']).query)).get('id')),
                   next(span.parent.stripped_strings, None))
                  for span in spans if (args.vpsid is None or span.text.startswith(args.vpsid))]
    except Exception:
        p.error("Couldn't parse URLs and IDs from:\n\t%s" % '\n\t'.join(span.parent for span in spans))

    if args.vpsid and len(parsed)==1:
        domain, url, vps_id, desc = parsed[0]
        url = urljoin(br.url, url)
        print("Found domain %s (%s) with VPS ID %d" % (domain, desc, vps_id))
    else:
        if args.vpsid is None:
            print("No VPS ID or domain name specified. List:")
        else:
            print("Found %d domains with names starting with %s. Specify one:" % (len(parsed), args.vpsid))
        for domain, baseurl, vps_id, desc in parsed:
            print("[%s]\t%s\n\t%s" % (vps_id, domain, desc))
        raise SystemExit(1)

########################################

def faux_json(t):
    if not (t.startswith('<JSONRESPONSE#') and t.endswith('#ENDJSONRESPONSE>')):
        raise ValueError("Did not receive expected JSON response")
    json = loads(t[14:-17])
    if json.get('result')=='success':
        return json
    raise RuntimeError("JSON response does not indicate success:\n\t%s" % json)

if args.action in ('boot','shutdown','reboot'):
    br.open('%s&json=true&mg-action=%sVM' % (url, args.action))
    try:
        faux_json(br.response.text)
    except (ValueError, RuntimeError) as e:
        p.error(e.args[0])

elif args.action=='passwd':
    p1, p2 = getpass("Enter new password: "), getpass("Retype new password: ")
    if p1!=p2:
        p.error("Passwords do not match")
    br.open('%s&json=true&mg-action=savePassword&newPassword=%s' % (url, quote(p1)))
    try:
        faux_json(br.response.text)
    except (ValueError, RuntimeError) as e:
        p.error(e.args[0])

elif args.action=='browse':
    print("Opening in browser: %s ..." % url)
    webbrowser.open(url)

elif args.action=='status':
    br.open(url)

    tbl = br.find("table", {'class':'table pm-stats'})
    print("VM status:")
    for tr in tbl.find_all('tr') if tbl else ():
        tds = tr.find_all('td')
        k, v = tds[0].text, ' '.join(tds[1].stripped_strings)
        if 'passw' in k.lower() and not args.show_passwords:
            v = '*' * len(v)
        print('\t%-20s : %s' % (k, v))

    tbl = br.find("table", {'class':'table table-striped accesscred'})
    print("Remote access credentials:")
    for tr in tbl.find_all('tr') if tbl else ():
        tds = tr.find_all('td')
        k, v = tds[0].text.rstrip(':'), ' '.join(tds[1].stripped_strings)
        if 'passw' in k.lower() and not args.show_passwords:
            v = '*' * len(v)
        print('\t%-20s : %s' % (k, v))

    hdr = br.find("h3", {'class':'panel-title'}, string='Options')
    print("Options:")
    for tr in hdr.parent.parent.find_all('div', {'class':'row'}) if hdr else ():
        tds = tr.find_all('div')
        k, v = tds[0].text.strip(), ' '.join(tds[1].stripped_strings)
        if 'passw' in k.lower() and not args.show_passwords:
            v = '*' * len(v)
        print('\t%-20s : %s' % (k, v))

elif args.action=='ssh':
    br.open('%s&mg-action=vnc' % url)
    applet = br.find('applet')
    sshdest = applet and applet.find('param', {'name':'jcterm.destinations'})
    strongs = br.find_all('strong')
    if not sshdest or len(strongs)!=2:
        p.error("Couldn't parse console page -- are you sure this is a Linux VPS?")

    console_host, console_port = sshdest['value'].split(':')
    console_password = strongs[1].text
    print("Linux system console can now be accessed via ssh:\n\n\tsshpass -p '%s' ssh -o StrictHostKeyChecking=no %s%s\n"
          % (console_password, ('' if console_port=='22' else '-p%s ' % console_port), console_host))

print("Success.")
