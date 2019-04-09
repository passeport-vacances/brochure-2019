#  Copyright 2019 Jacques Supcik
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

""" Commandline tool """

import logging
import shutil
import tempfile

import click

import brochure


@click.command()
@click.argument('db-url')
@click.option('--output', default="brochure.pdf")
@click.option('--debug/--no-debug', default=False)
@click.option('--verbose/--no-verbose', default=False)

def main(db_url, output, debug, verbose):
    """ Main """
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)

    data = brochure.get_data(db_url)
    f = tempfile.NamedTemporaryFile()  # pylint: disable=invalid-name
    brochure.gen_brochure(f, data)

    res = open(output, "wb")
    shutil.copyfileobj(f, res)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
