#!/usr/bin/env python3
import robobrowser
from urllib.parse import urlparse, parse_qsl, urljoin, urlencode
import webbrowser
import argparse
from getpass import getpass
import os

p = argparse.ArgumentParser(description='''
This is a tool to manage SolVPS virtual private servers directly from the command line.

It works by scraping the web-based user interface at https://www.solvps.com/secure/clientarea.php
''')
p.add_argument('vpsid', nargs='?', help="SolVPS numeric ID, or domain name")
p.add_argument('action', nargs='?', default='status', choices=('status','browse','boot','reboot','shutdown','ssh'),
               help="Action to perform on the VPS (ssh to console is only available for Linux systems)")
args = p.parse_args()

try:
    username, password = (l.strip() for l in open(os.path.expanduser('~/.solvps_credentials')))
except (IOError, ValueError):
    print("Could not read SolVPS credentials from ~/.solvps_credentials")
    print("File should contain username on the line #1, password on line #2.")
    username = input("SolVPS username: ")
    password = getpass("SolVPS password: ")

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

if args.vpsid is None:
    spans = br.find_all("span", {'class':'text-domain'})
    domain_url_desc = [(span.text, span.parent['href'], next(span.parent.stripped_strings, None)) for span in spans]

    print("No VPS ID or domain name specified. List:")
    for domain, baseurl, desc in domain_url_desc:
        vps_id = dict(parse_qsl(urlparse(baseurl).query)).get('id', '???')
        print("[%s]\t%s\n\t%s" % (vps_id, domain, desc))
    raise SystemExit(1)

elif args.vpsid.isdigit():
    vps_id = int(args.vpsid)
    url = 'https://www.solvps.com/secure/clientarea.php?action=productdetails&id=%d' % vps_id

else:
    span = br.find("span", {'class':'text-domain'}, text=args.vpsid)
    if span is None:
        p.error("Couldn't find domain %s under your services" % args.vpsid)

    try:
        url = urljoin(br.url, span.parent['href'])
        vps_id = int(dict(parse_qsl(urlparse(url).query)).get('id'))
    except Exception:
        p.error("Found domain %s, but couldn't parse ID from:\n\t%s" % (args.vpsid, span.parent))
    print("Found domain %s with VPS ID %d" % (args.vpsid, vps_id))

########################################

if args.action in ('boot','shutdown','reboot'):
    br.open('%s&json=true&mg-action=%sVM' % (url, args.action))
    if br.response.text.startswith('<JSONRESPONSE#') and br.response.text.endswith('#ENDJSONRESPONSE>'):
        json = br.response.text[14:-17]
        print(json)
    else:
        p.error("Did not receive expected JSON response")
elif args.action=='browse':
    print("Opening in browser: %s ..." % url)
    webbrowser.open(url)
elif args.action=='status':
    br.open(url)
    tbl = br.find("table", {'class':'table pm-stats'})
    print("VM status:")
    for tr in tbl.find_all('tr'):
        tds = tr.find_all('td')
        print('\t%-20s : %s' % (tds[0].text, ' '.join(tds[1].stripped_strings)))
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
