'''
Copyright 2019 Jacques Supcik

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----------------------------------------------------------------------------
Purpose: Generator for the brochure
Filename: brochure/__init__.py
Created Date: 2019-03-31
Author: Jacques Supcik
-----------------------------------------------------------------------------
'''

import dataclasses
import datetime
import json
import logging
import os
import pathlib
import re
import shutil
import subprocess
import tempfile

import jinja2
import records
import yaml

import groople
import j2latex

try:
    # pylint: disable=unused-import,ungrouped-imports
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    # pylint: disable=unused-import,ungrouped-imports
    from yaml import Loader, Dumper

# pylint: disable=invalid-name


logger = logging.getLogger(__name__)


def dump_data(data):
    """ Dump data (for debugging """
    class EnhancedJSONEncoder(json.JSONEncoder):
        """ Enhanced JSON for dataclasses """
        def default(self, o):  # pylint: disable=method-hidden
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

    print(json.dumps(data, cls=EnhancedJSONEncoder, indent=2))


def get_data(db_url):
    """ Returns data from the database """
    logger.debug("Reading data from groople")
    db = records.Database(db_url)
    config_file = pathlib.Path(pathlib.Path(__file__).parent, "config.yml")
    config = yaml.load(open(config_file, 'r'), Loader=Loader)
    return groople.get_all_activities(db, config)


def gen_brochure(dest_file, data, main="brochure"):
    """ Generates the brochure """
    # pylint: disable=too-many-locals
    logger.debug("generate brochure")
    meta_file = pathlib.Path(pathlib.Path(__file__).parent, "meta.yml")
    meta = yaml.load(open(meta_file, 'r'), Loader=Loader)

    template_dir = pathlib.Path(pathlib.Path(__file__).parent, "templates")
    dest_dir = tempfile.mkdtemp(prefix="brochure-")
    logger.debug("Output directory : %s", dest_dir)
    # agenda = groople.activities_to_agenda(data)

    env = j2latex.latex_env(jinja2.FileSystemLoader("/"))
    for root, _, files in os.walk(template_dir):
        for f in files:
            m = re.match(r'(.*)\.j2\.(.*)', f)
            if m:  # parse jinja2 template
                logger.debug("* Rendering %s", f)
                src = pathlib.Path(root, f)
                logger.debug("*** Source : %s", src)
                dst = pathlib.Path(root, '.'.join([m.group(1), m.group(2)]))
                dst = pathlib.Path(dest_dir, dst.relative_to(template_dir))
                logger.debug("*** Destination : %s", dst)

                dst.parent.mkdir(exist_ok=True, parents=True)

                template = env.get_template(str(src))
                dst.write_text(template.render(
                    categories=data,
                    date=datetime.datetime.now(),
                    meta=meta,
                    opts={
                        "light": False,
                        "one_per_page": True,
                        "draft": False,
                        "no_pub": True,
                        "no_intro": True,
                    }
                ))
            else:  # just copy file
                logger.debug("* Copying %s", f)
                src = pathlib.Path(root, f)
                dst = pathlib.Path(dest_dir, src.relative_to(template_dir))
                dst.parent.mkdir(exist_ok=True, parents=True)
                shutil.copyfile(src, dst)

    logger.debug("building pdf from tex latex files")

    res = subprocess.check_output(
        ["latexmk", "-xelatex", "-gg", "-silent", f"{main}.tex"],
        cwd=dest_dir
    )
    for i in res.decode("utf-8").splitlines():
        logger.debug(i)

    with open(pathlib.Path(dest_dir, f"{main}.pdf"), "rb") as src:
        shutil.copyfileobj(src, dest_file)
        dest_file.seek(0)

    shutil.rmtree(dest_dir)
