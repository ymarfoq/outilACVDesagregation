from boto.manage.server import Server
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(version="%prog 1.0", usage="Usage: %prog [options] instance-id [instance-id-2]")

    # Commands
    parser.add_option("-b", "--bucket", help="Destination Bucket", dest="bucket", default=None)
    parser.add_option("-p", "--prefix", help="AMI Prefix", dest="prefix", default=None)
    parser.add_option("-k", "--key", help="Private Key File", dest="key_file", default=None)
    parser.add_option("-c", "--cert", help="Public Certificate File", dest="cert_file", default=None)
    parser.add_option("-s", "--size", help="AMI Size", dest="size", default=None)
    parser.add_option("-i", "--ssh-key", help="SSH Keyfile", dest="ssh_key", default=None)
    parser.add_option("-u", "--user-name", help="SSH Username", dest="uname", default="root")
    parser.add_option("-n", "--name", help="Name of Image", dest="name")
    (options, args) = parser.parse_args()

    for instance_id in args:
        try:
            s = Server.find(instance_id=instance_id).next()
            print "Found old server object"
        except StopIteration:
            print "New Server Object Created"
            s = Server.create_from_instance_id(instance_id, options.name)
        assert(s.hostname is not None)
        b = s.get_bundler(uname=options.uname)
        b.bundle(bucket=options.bucket,prefix=options.prefix,key_file=options.key_file,cert_file=options.cert_file,size=int(options.size),ssh_key=options.ssh_key)
