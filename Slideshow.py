#!/usr/bin/python3
import gi
import os
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import GLib, Gdk, Gtk, WebKit2
from configparser import ConfigParser
import subprocess

import sys
import locale
from optparse import OptionParser

class SlideshowViewer(WebKit2.WebView):
    def __init__(self, path, locale='C', rtl=False, controls=False):
        self.path = path

        config = ConfigParser()
        config.read(os.path.join(self.path,'slideshow.conf'))

        slideshow_main = 'file://' + os.path.join(self.path, 'slides', 'index.html')

        parameters = []
        # slideshow_locale = self._find_available_locale(locale)
        slideshow_locale = self._find_available_locale("ko")
        parameters.append('locale=%s' % slideshow_locale)
        if rtl:
            parameters.append('rtl')
        if controls:
            parameters.append('controls')

        WebKit2.WebView.__init__(self)
        parameters_encoded = '&'.join(parameters)
        url = '%s#%s' % (slideshow_main, parameters_encoded)
        self.load_uri(url)
        print(url)

        settings = self.get_settings()
        settings.set_enable_write_console_messages_to_stdout(True)
        settings.set_allow_file_access_from_file_urls(True)
        self.set_settings(settings)

        config_width = int(config.get('Slideshow','width'))
        config_height = int(config.get('Slideshow','height'))
        self.set_size_request(config_width, config_height)

        self.connect('decide-policy', self._on_decide_policy)

    def _find_available_locale(self, locale):
        base_slides_dir = os.path.join(self.path, 'slides', 'l10n')
        extra_slides_dir = os.path.join(self.path, 'slides', 'extra')

        ll_cc = locale.split('.')[0]
        ll = ll_cc.split('_')[0]

        for slides_dir in [extra_slides_dir, base_slides_dir]:
            for test_locale in [locale, ll_cc, ll]:
                locale_dir = os.path.join(slides_dir, test_locale)
                if os.path.exists(locale_dir):
                    return test_locale
        return 'C'

    def _on_decide_policy(self, view, decision, decision_type):
        if decision_type == WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
            navigation_action = decision.get_navigation_action()
            request = navigation_action.get_request()
            uri = request.get_uri()
            decision.use()
        return False

if __name__ == '__main__':
    # Gdk.threads_init()

    default_path = os.path.join( os.path.abspath(os.path.dirname(sys.argv[0])) , 'build', 'ubuntu' )
    default_locale = locale.getlocale()[0]
    
    parser = OptionParser(usage="usage: %prog [options] [slideshow]")
    parser.add_option("-l", "--locale", help="LOCALE to use for the slideshow", metavar="LOCALE", default=default_locale)
    parser.add_option("-r", "--rtl", action="store_true", help="use output in right-to-left format")
    parser.add_option("-c", "--controls", action="store_true", help="Enable controls in the slideshow (you may need to resize the window)")
    parser.add_option("-p", "--path", help="path to the SLIDESHOW which will be presented", metavar="SLIDESHOW", default=default_path)

    (options, args) = parser.parse_args()
    options.path = os.path.abspath(options.path)

    slideshow_window = Gtk.Window()
    slideshow_window.set_title("Ubiquity Slideshow")
    slideshow_window.connect('destroy',Gtk.main_quit)
    slideshow_window.set_resizable(False)

    slideshow_container = Gtk.VBox()
    slideshow_window.add(slideshow_container)

    slideshow = SlideshowViewer(options.path, locale=options.locale, rtl=options.rtl, controls=options.controls)

    slideshow_container.add(slideshow)
    slideshow_window.show_all()

    Gtk.main()
