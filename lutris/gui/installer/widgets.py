from gi.repository import Gtk, Pango


class InstallerLabel(Gtk.Label):
    """A label for installers"""

    def __init__(self, text, wrap=True):
        super().__init__()
        if wrap:
            self.set_line_wrap(True)
            self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        else:
            self.set_property("ellipsize", Pango.EllipsizeMode.MIDDLE)
        self.set_alignment(0, 0.5)
        self.set_margin_right(12)

        #Find and replace URLs with clickable links
        url_regex = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        parsed_text = url_regex.sub(lambda url: f'<a href="{url.group()}">{url.group()}</a>', text)

        self.set_markup(parsed_text)
        self.props.can_focus = False
        self.set_tooltip_text(text)
