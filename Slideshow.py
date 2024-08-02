#!/usr/bin/python3
import gi
import os

# Adjust the version to match the available version on your system
gi.require_version('WebKit2', '4.1')
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
        config.read(os.path.join(self.path, 'slideshow.conf'))

        slideshow_main = 'file://' + os.path.join(self.path, 'slides', 'index.html')

        parameters = []
        slideshow_locale = self._find_available_locale(locale)
        parameters.append('locale=%s' % slideshow_locale)
        if rtl:
            parameters.append('rtl')
        if controls:
            parameters.append('controls')

        context = WebKit2.WebContext.get_default()
        context.set_cache_model(WebKit2.CacheModel.DOCUMENT_VIEWER)
        WebKit2.WebView.__init__(self)
        parameters_encoded = '&'.join(parameters)
        url = '%s#%s' % (slideshow_main, parameters_encoded)
        self.load_uri(url)
        print(url)

        settings = self.get_settings()
        settings.set_property('allow-file-access-from-file-urls', True)

        config_width = int(config.get('Slideshow', 'width'))
        config_height = int(config.get('Slideshow', 'height'))
        self.set_size_request(config_width, config_height)

        self.connect('context-menu', self.on_context_menu)
        self.connect('decide-policy', self.on_slideshow_link_clicked)

    def on_context_menu(self, unused_web_view, unused_context_menu,
                        unused_event, unused_hit_test_result):
        return True

    def on_slideshow_link_clicked(self, web_view, decision, decision_type):
        gi.require_version('WebKit2', '4.1')
        from gi.repository import WebKit2
        if decision_type == WebKit2.PolicyDecisionType.NEW_WINDOW_ACTION:
            request = decision.get_request()
            uri = request.get_uri()
            decision.ignore()
            misc.launch_uri(uri)
            return True
        return False

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

def progress_increment(progressbar, fraction):
    new_fraction = progressbar.get_fraction() + fraction
    if new_fraction > 1:
        progressbar.set_fraction(1.0)
        return False

    progressbar.set_fraction(new_fraction)
    return True

default_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'build', 'ubuntu')
default_locale = locale.getlocale()[0]

parser = OptionParser(usage="usage: %prog [options] [slideshow]")
parser.add_option("-l", "--locale", help="LOCALE to use for the slideshow", metavar="LOCALE", default=default_locale)
parser.add_option("-r", "--rtl", action="store_true", help="use output in right-to-left format")
parser.add_option("-c", "--controls", action="store_true", help="Enable controls in the slideshow (you may need to resize the window)")
parser.add_option("-p", "--path", help="path to the SLIDESHOW which will be presented", metavar="SLIDESHOW", default=default_path)

(options, args) = parser.parse_args()
options.path = os.path.abspath(options.path)
if not os.path.exists(options.path):
    print("\033[91m * Please build the slideshow content first by using the make command * \033[0m")
    sys.exit()

slideshow_window = Gtk.Window()
slideshow_window.set_title("Ubiquity Slideshow with Webkit")
slideshow_window.connect('destroy', Gtk.main_quit)
slideshow_window.set_resizable(False)

slideshow_container = Gtk.VBox()
slideshow_window.add(slideshow_container)

slideshow = SlideshowViewer(options.path, locale=options.locale, rtl=options.rtl, controls=options.controls)

install_progressbar = Gtk.ProgressBar()
install_progressbar.set_margin_top(8)
install_progressbar.set_margin_end(8)
install_progressbar.set_margin_bottom(8)
install_progressbar.set_margin_start(8)
install_progressbar.set_fraction(0)

slideshow_container.add(slideshow)
slideshow_container.add(install_progressbar)

slideshow_container.set_child_packing(install_progressbar, True, False, 0, 0)

slideshow_window.show_all()

Gtk.main()
