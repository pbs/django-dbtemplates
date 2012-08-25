#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Django management command to watch and load dbtemplates from a directory.

The command does not sync bidirectionally, nor does it read files and save
templates upon startup.  It only modifies database records when it is running
and when those files under its watched directory are changed.

"""
from logging import basicConfig, INFO, info, warn
from os import path
from sys import exit, platform
from time import sleep

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from dbtemplates.models import Template


# Attempt to load a file system notification/event library, falling through
# if none is available.
linux_impl = macos_impl = have_impl = False
try:
    from pyinotify import ProcessEvent, WatchManager, Notifier, IN_CLOSE_WRITE
    have_impl = linux_impl = True
except (ImportError, ):
    pass

try:
    from fsevents import Observer, Stream
    have_impl = macos_impl = True
except (ImportError, ):
    pass


class Command(BaseCommand):
    help = 'Monitors a directory and updates the database when files change.'

    def handle(self, *args, **options):
        """Framework hook for running the routine via the management command.

        This routine is a wrapper around the `main` function with keyboard
        interrupt trapping.
        """
        # When no file system notifier was imported, check the platform and
        # raise an error with a message about which to install.
        if not have_impl:
            if platform == 'darwin':
                raise CommandError('Install MacFSEvents to use this command')
            elif platform == 'linux2':
                raise CommandError('Install pyinotify to use this command')
            else:
                raise CommandError('This command is not supported on your platform')

        # When no directory is given, raise an error.
        if not args:
            raise CommandError('Directory argument required')

        # When the given argument does not exist, or if it is not a directory,
        # raise an error.
        watchpath = args[0]
        if not path.exists(path.abspath(watchpath)):
            raise CommandError('Directory does not exist')
        if not path.isdir(watchpath):
            raise CommandError('Argument is not a directory')

        # Run the implementation-specific routine.
        basicConfig(level=INFO)
        try:
            main(watchpath)
        except (KeyboardInterrupt, ):
            pass


class fs(object):
    """Format strings referenceable as class attributes."""
    changed = 'file changed name=%s, path=%s'
    notmpl = 'template with name %s does not exist in database'
    saved = 'saved template name=%s, id=%s'
    start = 'monitoring %s for changes (Control+C to exit)'


if linux_impl:
    # This is the Linux platform implementation of our monitor.  We use a subclass
    # of pyinotify.Process event for handling post-write file events, and our main
    # routine sets up the various pyinotify objects.

    def main(watchdir):
        """Main callable for Linux; uses pyinotify library to process events."""
        watcher = WatchManager()
        handler = OnModify(watchdir)
        notifier = Notifier(watcher, handler)
        watcher.add_watch(watchdir, IN_CLOSE_WRITE, rec=True, auto_add=True)
        info(fs.start, watchdir)
        notifier.loop()

    class OnModify(ProcessEvent):
        def __init__(self, base):
            self.base = path.abspath(base)

        def process_IN_CLOSE_WRITE(self, event):
            info(fs.changed, event.name, event.path)
            full = path.abspath('{0}/{1}'.format(event.path, event.name))
            match = full[1+len(self.base):]
            try:
                template = Template.objects.get(name=match)
            except (Template.DoesNotExist, ):
                template = None
            if template:
                template.content = open(full).read()
                template.save()
                info(fs.saved, match, template.id)
            else:
                warn(fs.notmpl, match)



if macos_impl:
    # This is the MacOS platform implementation of our monitor.  We use a closure
    # to construct a callback that is invoked to handle all events.  The closure
    # checks the event for it's mask and only processes file modification events.
    # Our main routine sets up the various MacFSEvents objects.

    def main(watchdir):
        """Main callable for MacOS; uses MacFSEvents library for processing."""
        callback = make_callback(watchdir)
        observer = Observer()
        stream = Stream(callback, watchdir, file_events=True)
        observer.schedule(stream)
        base = path.abspath(watchdir)
        info(fs.start, watchdir)
        try:
            # This form is necessary to allow the user to interrupt the command.
            # The code shown in the docs don't allow C+c handling, so we use a
            # small sleep loop to allow it.
            observer.start()
            while True:
                sleep(0.5)
        except (KeyboardInterrupt, ):
            observer.stop()


    def make_callback(watchdir):
        base = path.abspath(watchdir)
        modify_event = 2

        def callback(event):
            if event.mask != modify_event:
                return
            info(fs.changed, event.name, event.mask)
            full = event.name
            match = full[1+len(base):]
            try:
                template = Template.objects.get(name=match)
            except (Template.DoesNotExist, ):
                template = None
            if template:
                template.content = open(full).read()
                template.save()
                info(fs.saved, match, template.id)
            else:
                warn(fs.notmpl, match)
        return callback
