#!/usr/bin/env python
# Modified from
# http://tech.adroll.com/blog/ops/2013/09/30/dns-less-setup-in-aws.html

import os
from optparse import OptionParser

from boto import ec2
from boto.s3.connection import S3Connection
from boto.s3.key import Key

def put_file(bucket, key_name, content):
    k = Key(bucket)
    k.key = key_name
    k.set_contents_from_string(content,
                               {'Content-Type': 'text/plain'},
                               replace=True)

def main(options):
    aws_api_key = options.aws_access_key
    aws_secret_key = options.aws_secret_key
    os.environ['AWS_ACCESS_KEY_ID'] = options.aws_access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = options.aws_secret_key
    #regions = ['us-west-1', 'us-west-2', 'us-east-1', 'eu-west-1', 'ap-southeast-1']
    regions = ['eu-west-1', 'ap-southeast-1']

    region_instances = {}
    for region in regions:
        conn = ec2.connect_to_region(region)
        all_reservations = conn.get_all_instances(filters={ 'tag-key': 'dns' })

        instances = {}
        for reservation in all_reservations:
            for instance in reservation.instances:
                if instance.state == "running" and 'dns' in instance.tags:
                    for dns_name in instance.tags['dns'].strip().split(","):
                        instances[dns_name] = instance

        region_instances[region] = instances

    #Generate an etc host for each region, local instances using 10. and others using public
    hosts_lines = [
        '127.0.0.1 localhost',
        '::1 ip6-localhost ip6-loopback',
        'fe00::0 ip6-localnet',
        'ff00::0 ip6-mcastprefix',
        'ff02::1 ip6-allnodes',
        'ff02::2 ip6-allrouters',
        'ff02::3 ip6-allhosts'
    ]

    #Generate an etc hosts with all public ip addresses, for developers
    hosts_lines = []
    for region in regions:
        for dns_name,instance in region_instances[src_region].iteritems():
            print("INSTANCE:", instance, dir(instance))
            hosts_lines.append("%s %s %s.internal" % (instance.ip_address, dns_name, dns_name))

    # make sure we replace hosts file as atomically as possible.
    with open("etc_hosts", "w") as outf:
        outf.write("\n".join(hosts_lines))


if __name__ == '__main__':
    """
    e.g, update_hosts.py --secret=<SECRET_KEY> --api=<API_KEY>
    """
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("--secret", action="store", dest="aws_secret_key",
                        default=os.environ.get('AWS_SECRET_ACCESS_KEY'), help="AWS Secret Access Key")
    parser.add_option("--api", action="store", dest="aws_access_key",
                        default=os.environ.get('AWS_ACCESS_KEY_ID'), help="AWS Access Key")
    (options, args) = parser.parse_args()

    main(options)
