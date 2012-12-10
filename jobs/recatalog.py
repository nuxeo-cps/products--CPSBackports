# Copyright (c) 2012 CPS-CMS Community <http://cps-cms.org>
#
# Author: Georges Racinet <gracinet@cps-cms.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation or (at your convenience) any other version
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
"""Resync various persistent stuff: tree caches, catalog..."""

import logging
import os
import csv
from pprint import pformat

from DateTime import DateTime
from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('CPSBackports.jobs.recatalog')
from Products.CPSUtil import cpsjob
from Products.CPSBackports.abstract import commit

class Reindexer:

    def __init__(self, portal, options, errors_file=''):
        self.portal = portal
        self.commit_every = getattr(options, 'commit_every', 10)
        if errors_file:
            self.errors_file = open(errors_file, 'w')
            self.errors_writer = csv.DictWriter(self.errors_file,
                                                ('rpath', 'reason'))
            self.dump_errors = True
        else:
            self.dump_errors = False

        self.pxtool = getToolByName(portal, 'portal_proxies')
        self.catalog = getToolByName(portal, 'portal_catalog')
        self.total_proxies = len(self.pxtool._rpath_to_infos)

    def log_progress(self, done):
        now = DateTime()
        elapsed_mn = (now-self.start_time) * 1440

        total = self.total_proxies
        logger.info("Reindexed %d over %d (%2d%%) in %d minutes "
                    "(ETA %d minutes)",
                    done, total, (100*done)/total,
                    elapsed_mn, total*elapsed_mn/done)

    def log_faulty(self, rpath, reason=''):
        if not self.dump_errors:
            return
        self.errors_writer.writerow(dict(rpath=rpath, reason=reason))
        self.errors_file.flush()

    def batch_log_faulty(self, rpaths, reason=''):
        for rpath in rpaths:
            self.log_faulty(rpath, reason=reason)

    def reindex(self):
        self.start_time = DateTime()
        current_batch = []

        for i, rpath in enumerate(self.pxtool._rpath_to_infos.keys()):
            proxy = self.portal.unrestrictedTraverse(rpath, None)

            if proxy is None:
                self.log_faulty(rpath, reason="Unreacheable object")
                continue

            proxy_path = '/'.join(proxy.getPhysicalPath())
            self.catalog.catalog_object(proxy, proxy_path)
            current_batch.append(rpath)

            if i and not (i % self.commit_every):
                self.log_progress(i)
                try:
                    commit()
                except Exception, exc:
                    self.batch_log_faulty(current_batch, reason=str(exc))
                current_batch = []


def job(portal, args, options):
    """CPS job bootstrap"""

    parser = cpsjob.optparser
    if args:
        parser.error("Args: %s; this job accepts options only. "
                     "Try --help" % args)

    efile = options.errors_file
    if efile and os.path.exists(efile):
        parser.error("file already exists: %r. "
                     "Not willing to overwrite" % efile)

    reindexer = Reindexer(portal, options, errors_file=efile)
    reindexer.reindex()

# invocation through zopectl run
if __name__ == '__main__':
    optparser = cpsjob.optparser
    optparser.add_option('--index-from',
                         help="Relative path to index from")
    optparser.add_option('--commit-every',
                         default=10,
                         help="Number of proxies to perform commit.")
    optparser.add_option('--errors-file',
                         default='',
                         help="If specified, will dump errors in CSV "
                         "format to the specified file.")
    optparser.add_option('--input-file',
                         help="If specified, will reindex proxies from "
                         "that input file. CSV format is assumed, with "
                         "first column being the relative path from portal")

    cpsjob.run(app, job)

