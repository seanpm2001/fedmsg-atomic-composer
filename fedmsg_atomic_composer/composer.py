import subprocess
import fedmsg.consumers

from twisted.internet import inotify
from twisted.python import filepath


class AtomicComposer(fedmsg.consumers.FedmsgConsumer):
    topic = ['org.fedoraproject.prod.bodhi.updates.fedora.sync',
             'org.fedoraproject.prod.compose.branched.rsync.complete',
             'org.fedoraproject.prod.compose.rawhide.rsync.complete']
    config_key = 'ostreecomposer'

    def __init__(self, hub, *args, **kw):
        super(AtomicComposer, self).__init__(hub, *args, **kw)
        self.config = hub.config

    def consume(self, msg):
        self.log.debug(msg)
        body = msg['body']
        topic = body['topic']

        if 'rawhide' in topic:
            arch = body['msg']['arch']
            self.log.info('New rawhide %s compose ready', arch)
        elif 'branched' in topic:
            arch = body['msg']['arch']
            branch = body['msg']['branch']
            self.log.info('New %s %s branched compose ready', branch, arch)
            log = body['msg']['log']
            if log != 'done':
                self.log.warn('Compose not done?')
                return
        elif 'updates' in topic:
            release = body['msg']['release']
            repo = body['msg']['repo']
            self.log.info('New %s %s compose ready', release, repo)

        # Trigger the rpm-ostree taskrunner
        self.call(['touch', self.config['touch_file']])

        # ostree compose
        # extract summary
        # inject summary into repodata

    def call(self, cmd, **kwargs):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kwargs)
        out, err = p.communicate()
        return out, err, p.returncode