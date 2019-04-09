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

""" The groople module contains code to deal with the Groople Database """

import re

from .activity import Activity
from .category import Category
from .group import Group


# pylint: disable=invalid-name


def get_attribute_map(db, table, config):
    """ Returns the attribute map """
    attr_id = dict()
    rows = db.query(f'select * from {table}')
    for r in rows:
        t = [k for (k, v) in config.items() if re.match(v, r.attribute_label)]
        if len(t) > 1:
            raise Exception("Internal error")
        if len(t) == 1:
            attr_id[r.attribute_id] = t[0]
    return attr_id


def get_all_activities(db, config):
    """ Returns all activities """
    # pylint: disable=too-many-branches
    categories = dict()
    activities = dict()
    groups = dict()

    rows = db.query('select * from categories')
    for r in rows:
        c = Category(r.id, r.label, r.order_field, list())
        categories[r.id] = c

    rows = db.query('select * from activities')
    for r in rows:
        if r.enabled != 0 and r.activity_label != "DUMMY":
            a = Activity(
                r.activity_id, r.activity_label, r.information, r.category_id, dict(), list()
            )
            activities[r.activity_id] = a
            c = categories.get(r.category_id, None)
            c.activities.append(a)

    aam = get_attribute_map(db, '_activity_attributes', config['activity_attributes'])
    muam = get_attribute_map(db, '_user_attributes', config['multiple_user_attributes'])
    gam = get_attribute_map(db, '_group_attributes', config['group_attributes'])

    rows = db.query('select * from activities_attributes')
    for r in rows:
        if r.activity_id in activities:
            a = activities[r.activity_id]
            key = aam.get(r.attribute_id, None)
            if key is not None:
                a.attributes[key] = r.value

    rows = db.query('select * from activities_users_attributes_values')
    for r in rows:
        if r.activity_id in activities:
            a = activities[r.activity_id]
            key = muam.get(r.user_attribute_id, None)
            if key is not None:
                a.attributes[key] = a.attributes.get(key, list()) + [r.attribute_value]

    rows = db.query('select * from groups')
    for r in rows:
        if r.group_active == 'T':
            g = Group(r.group_id, r.group_label, r.maxQuota)
            groups[r.group_id] = g
            if r.activity_id in activities:
                activities[r.activity_id].groups.append(g)

    rows = db.query('select * from groups_attributes')
    for r in rows:
        if r.group_id in groups:
            g = groups[r.group_id]
            key = gam.get(r.attribute_id, None)
            if key is not None:
                g.attributes[key] = r.value

    # Fix/complete groups
    for g in groups.values():
        g.sanitize()

    # Fix/complete activities and sort groups
    for a in activities.values():
        a.sanitize()
        a.sort_groups()

    # sort all activities
    for c in categories.values():
        c.sort_activities()

    return sorted(categories.values(), key=lambda x: x.order)


def activities_to_agenda(categories):
    """ Returns an agenda from the activities """
    # TODO! WIP  # pylint: disable=fixme
    allpass = list()
    agenda = dict()
    for c in categories:
        for a in c.activities:
            if a.attributes.get("all_pass", False):
                allpass.append(a)
                continue
            gi = 0
            for g in a.groups:
                gi += 1
                for d in g.days:
                    if d["day"] is None or d["month"] is None:
                        print(f"Ignoring {a.name}")
                        continue
                    key = (d["day"], d["month"])
                    value = (a, d['schedule'], d['order'], gi, len(a.groups))

                    if key not in agenda:
                        agenda[key] = list()

                    if value not in agenda[key]:
                        agenda[key].append(value)

    res = list()
    for i in sorted(agenda.keys(), key=lambda x: x[0] * 32 + x[1]):
        res.append({
            "id": i,
            "activities": sorted(agenda[i], key=lambda x: x[2]),
        })

    for i in res:
        print(f"Date : {i['id'][0]}.{i['id'][1]}")
        for j in i['activities']:
            print(f"{j[0].name} {j[3]}/{j[4]} -> {j[1]}")

    return res
