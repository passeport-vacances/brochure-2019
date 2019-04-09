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

""" Flask Web App (REST API) """

import os
import tempfile

import flask
from flask import Flask
from flask.logging import create_logger
from py3wetransfer import Py3WeTransfer

import brochure

app = Flask(__name__)  # pylint: disable=invalid-name
LOG = create_logger(app)


@app.route('/check')
def check():
    """ Check if the service is running (to help Dokku) """
    return "OK\n"


@app.route('/bons-a-tirer')
def bons_a_tirer():
    """ Generate the "bons-à.tirer" """
    apikey = os.getenv("WE_KEY")
    if apikey is None:
        raise Exception("Please, define the we API KEY in the WE_KEY environment variable")

    db_url = os.getenv("DB_URL")
    if apikey is None:
        raise Exception("Please, define the we Database URL in the DB_URL environment variable")

    data = brochure.get_data(db_url)
    tmp = tempfile.NamedTemporaryFile(prefix="pvfr-bons-a-tirer-", suffix=".pdf")
    brochure.gen_brochure(tmp, data)

    LOG.debug("Uploading to we-transfer")
    we = Py3WeTransfer(apikey)  # pylint: disable=invalid-name
    url = we.upload_file(tmp.name, "Passeport vacances Fribourg, bons à tirer 2019")
    LOG.debug("URL : %s", url)
    tmp.close()

    return flask.jsonify({
        'success': True,
        'url': url
    })


if __name__ == '__main__':
    app.run()
