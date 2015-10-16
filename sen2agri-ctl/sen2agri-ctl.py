#!/usr/bin/env python
from __future__ import print_function
import argparse
import dbus
import json
import numbers
import sys


class Site(object):

    def __init__(self, site_id, name):
        self.site_id = site_id
        self.name = name

    def __cmp__(self, other):
        if hasattr(other, 'site_id'):
            return self.site_id.__cmp__(other.site_id)


class ConfigurationValue(object):

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return str({"key": self.key, "value": self.value})

    def __repr__(self):
        return str(self)

    def to_dbus(self):
        return dbus.Struct([self.key, self.value])


class ConfigurationValueList(object):

    def __init__(self, values):
        self.values = values

    def __str__(self):
        return str(self.values)

    def to_dbus(self):
        return map(lambda cv: cv.to_dbus(), self.values)


class NewJob(object):

    def __init__(self, name, description, processor_id, site_id, start_type,
                 parameters, configuration):
        self.name = name
        self.description = description
        self.processor_id = processor_id
        self.site_id = site_id
        self.start_type = start_type
        self.parameters = parameters
        self.configuration = configuration

    def to_dbus(self):
        return dbus.Struct([self.name, self.description, self.processor_id,
                            self.site_id, self.start_type, self.parameters,
                            self.configuration.to_dbus()])


class Sen2AgriClient(object):

    def __init__(self):
        bus = dbus.SystemBus()
        self.proxy = bus.get_object('org.esa.sen2agri.persistenceManager',
                                    '/org/esa/sen2agri/persistenceManager')

    def get_sites(self):
        sites = []
        for site in self.proxy.GetConfigurationSet()[3]:
            sites.append(Site(int(site[0]), str(site[1])))

        return sorted(sites)

    def submit_job(self, job):
        self.proxy.SubmitJob(job.to_dbus())


class Sen2AgriCtl(object):

    def __init__(self):
        self.client = Sen2AgriClient()

        parser = argparse.ArgumentParser(
            description="Controls the Sen2Agri system")
        subparsers = parser.add_subparsers()

        parser_list_sites = subparsers.add_parser(
            'list-sites', help="Lists the available sites")
        parser_list_sites.set_defaults(func=self.list_sites)

        parser_submit_job = subparsers.add_parser(
            'submit-job', help="Submits a new job")
        parser_submit_job.add_argument('-s', '--site',
                                       required=True, help="site")
        parser_submit_job_subparsers = parser_submit_job.add_subparsers()

        parser_crop_mask = parser_submit_job_subparsers.add_parser(
            'crop-mask', help="Submits a new crop mask job")
        parser_crop_mask.add_argument('-i', '--input',
                                      nargs='+', required=True,
                                      help='input products')
        parser_crop_mask.add_argument('-r', '--reference',
                                      required=True, metavar="SHAPEFILE",
                                      help="reference polygons")
        parser_crop_mask.add_argument(
            '--date-start',
            required=True, help="temporal resampling start date (YYYYMMDD)")
        parser_crop_mask.add_argument(
            '--date-end',
            required=True, help="temporal resampling end date (YYYYMMDD)")
        parser_crop_mask.add_argument(
            '--resolution', type=int, help="resolution in m")
        parser_crop_mask.add_argument(
            '-p', '--parameter', action='append', nargs=2,
            metavar=('KEY', 'VALUE'), help="override configuration parameter")
        parser_crop_mask.set_defaults(func=self.submit_crop_mask)

        parser_crop_type = parser_submit_job_subparsers.add_parser(
            'crop-type', help="Submits a new crop type job")
        parser_crop_type.add_argument('-i', '--input',
                                      nargs='+', required=True,
                                      help="input products")
        parser_crop_type.add_argument(
            '-r', '--reference',
            required=True, metavar="SHAPEFILE", help="reference polygons")
        parser_crop_type.add_argument(
            '--date-start',
            required=True, help="temporal resampling start date (YYYYMMDD)")
        parser_crop_type.add_argument(
            '--date-end',
            required=True, help="temporal resampling end date (YYYYMMDD)")
        parser_crop_type.add_argument(
            '--crop-mask', help="crop mask")
        parser_crop_type.add_argument(
            '--resolution', type=int, help="resolution in m")
        parser_crop_type.add_argument(
            '-p', '--parameter', action='append', nargs=2,
            metavar=('KEY', 'VALUE'), help="override configuration parameter")
        parser_crop_type.set_defaults(func=self.submit_crop_type)

        args = parser.parse_args(sys.argv[1:])
        args.func(args)

    def list_sites(self, args):
        for site in self.client.get_sites():
            print("{} {}".format(site.site_id, site.name))

    def submit_crop_mask(self, args):
        parameters = {'input_products': args.input,
                      'reference_polygons': args.reference,
                      'date_start': args.date_start,
                      'date_end': args.date_end}

        if args.resolution:
            parameters['resolution'] = args.resolution

        job = self.create_job(4, parameters, args)
        self.client.submit_job(job)

    def submit_crop_type(self, args):
        parameters = {'input_products': args.input,
                      'reference_polygons': args.reference,
                      'date_start': args.date_start,
                      'date_end': args.date_end}

        if args.crop_mask:
            parameters['crop_mask'] = args.crop_mask
        if args.resolution:
            parameters['resolution'] = args.resolution

        job = self.create_job(5, parameters, args)
        self.client.submit_job(job)

    def create_job(self, processor_id, parameters, args):
        config = config_from_parameters(args.parameter)

        site_id = self.get_site_id(args.site)
        if site_id is None:
            raise RuntimeError("Invalid site '{}'".format(args.site))

        job = NewJob("", "", processor_id, site_id, 2,
                     json.JSONEncoder().encode(parameters), config)
        return job

    def get_site_id(self, name):
        if isinstance(name, numbers.Integral):
            return name

        sites = self.client.get_sites()
        for site in sites:
            if site.name == name:
                return site.site_id

        return None


def config_from_parameters(parameters):
    config = []
    if parameters:
        for param in parameters:
            config.append(ConfigurationValue(param[0], param[1]))
    return ConfigurationValueList(config)

if __name__ == '__main__':
    try:
        Sen2AgriCtl()
    except Exception, err:
        print("ERROR:", err, file=sys.stderr)