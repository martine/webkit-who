#!/usr/bin/python

import re
import subprocess

def parse_log(since='6 months ago'):
    """Parse the commit log, yielding (date, author email) pairs.

    Parser is WebKit-aware: it knows the committer frequently isn't
    the author.

    |since| is an argument for the --since flag to git log.
    """

    commit_re = re.compile('^commit ')
    author_re = re.compile('^Author: (\S+)')
    date_re = re.compile('^Date:\s+(\S+)')
    # Regexp for a ChangeLog header: date + author name + author email.
    changelog_re = re.compile('^    \d\d\d\d-\d\d-\d\d  .+?  <(.+?)>')
    # Regexp for a in-ChangeLog commit message.
    patch_re = re.compile('^    Patch by .+? <([^>]+?)> on \d\d\d\d-\d\d-\d\d')

    log = subprocess.Popen(['git', 'log', '--date=short', '--since=' + since],
                           stdout=subprocess.PIPE)
    n = 0
    for line in log.stdout.xreadlines():
        if commit_re.match(line):
            if n > 0:
                if ' and ' in author:
                    author = author[0:author.find(' and ')]
                yield date, author
            author = None
            date = None
            n += 1
            continue
        match = author_re.match(line)
        if match:
            author = match.group(1)
            continue
        match = date_re.match(line)
        if match:
            date = match.group(1)
            continue
        match = changelog_re.match(line)
        if match:
            author = match.group(1)
            continue
        match = patch_re.match(line)
        if match:
            author = match.group(1)
            continue

# See:  http://trac.webkit.org/wiki/WebKit%20Team

# Mapping of domain name => company name.
domain_companies = {
    'chromium.org': 'google',
    'google.com': 'google',
    'apple.com': 'apple',
    'igalia.com': 'igalia',
    'nokia.com': 'nokia',
    'trolltech.com': 'nokia',
    'torchmobile.com.cn': 'torch mobile',
    'torchmobile.com': 'torch mobile',
    'rim.com': 'rim',
    'appcelerator.com': 'appcelerator',
    'inf.u-szeged.hu': 'u-szeged.hu',
    'stud.u-szeged.hu': 'u-szeged.hu',
    'ericsson.com': 'ericsson.com',
}

# Lists of particular names known to be in some companies.
other = {
    'google': [
        'abarth@webkit.org',
        'antonm@chromium',
        'christian.plesner.hansen@gmail.com',  # v8
        'eric@webkit.org',
        'jens@mooseyard.com',
        'joel@jms.id.au',  # intern
        'kinuko@chromium.com',
        'rniwa@webkit.org',  # intern
        'shinichiro.hamaji@gmail.com',
        'yaar@chromium.src',
    ],

    'apple': [
        'ap@webkit.org',
        'sam@webkit.org',
    ],

    'redhat': [
        'danw@gnome.org',
        'otte@webkit.org',
    ],

    'nokia': [
        'hausmann@webkit.org',
        'kenneth@webkit.org',
        'tonikitoo@webkit.org',
        'vestbo@webkit.org',
        'faw217@gmail.com',  # A guess, based on commits.
        'girish@forwardbias.in',  # Appears to be consulting for Qt = Nokia(?).
        'norbert.leser&nokia.com',
    ],

    'rim': [
        'dbates@webkit.org',
        'zimmermann@webkit.org',
    ],

    'misc': [
        'bfulgham@webkit.org',  # WinCairo
        'chris.jerdonek@gmail.com',  # Seems to be doing random script cleanups?
        'jmalonzo@webkit.org',  # GTK
        'joanmarie.diggs@gmail.com',  # GTK Accessibility (Sun?)
        'joepeck@webkit.org',   # Inspector.
        'krit@webkit.org',
        'ossy@webkit.org',
        'simon.maxime@gmail.com',  # Haiku
        'skyul@company100.net',  # BREWMP
        'zandobersek@gmail.com',  # GTK
        'zecke@webkit.org',  # GTK+Qt
        'zoltan@webkit.org',
        'christian@twotoasts.de',  # GTK, Midori
    ]
}

# One-off mapping of names to companies.
people_companies = {
    'martin.james.robinson@gmail.com': 'appcelerator',
    'xan@webkit.org': 'igalia',
    'kevino@webkit.org': 'wx',
    'kov@webkit.org': 'collabora',
    'ariya@webkit.org': 'qualcomm',
}


email_sets = [
    ['xan@webkit.org', 'xan@gnome.org'],
    ['kevino@webkit.org', 'kevino@theolliviers.com'],
    ['kov@webkit.org', 'gustavo.noronha@collabora.co.uk', 'gns@gnome.org'],
    ['ariya@webkit.org', 'ariya.hidayat@gmail.com'],
    ['mbelshe@chromium.org', 'mike@belshe.com'],
    ['joepeck@webkit.org', 'joepeck02@gmail.com'],
    ['zecke@webkit.org', 'zecke@selfish.org'],
    ['dbates@webkit.org', 'dbates@intudata.com'],
    ['tonikitoo@webkit.org', 'antonio.gomes@openbossa.org'],
    ['kenneth@webkit.org', 'kenneth.christiansen@openbossa.org'],
    ['otte@webkit.org', 'otte@gnome.org'],
    ['abarth@webkit.org', 'abarth'],
    ['finnur@chromium.org', 'finnur.webkit@gmail.com'],
    ['atwilson@chromium.org', 'atwilson@atwilson-macpro.local'],
]
canon_map = {}

def canonicalize_email(email):
    global canon_map
    if not canon_map:
        for emails in email_sets:
            for email in emails[1:]:
                canon_map[email] = emails[0]

    if email in canon_map:
        return canon_map[email]
    return email


def classify_email(email):
    """Given an email, return a string identifying their company."""
    domain = None
    if '@' in email:
        _, domain = email.split('@')
    if domain:
        if domain in domain_companies:
            return domain_companies[domain]
        if domain.endswith('.google.com'):
            return 'google'
    if email in people_companies:
        return people_companies[email]

    for company, people in other.iteritems():
        if email in people:
            return company

    return 'unknown'
