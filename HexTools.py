import sublime
import sublime_plugin


class HexEditor():
    def __init__(self, edit):
        self.edit = edit
        self.view = sublime.active_window().active_view()

    def load_file(self):
        fname = self.view.file_name()
        reg = sublime.Region(0, self.view.size())
        self.view.erase(self.edit, reg)
        f = open(fname, 'rb')
        bfile = f.read()
        f.close()

        i = 0
        hexbytes = ''
        strbytes = ''
        pos = 0
        for b in bfile:
            i += 1
            hexbytes += "%02X " % ord(b)
            if b.isalnum():
                strbytes += b
            else:
                strbytes += '.'
            if i % 16 == 0:
                self.view.insert(self.edit, self.view.size(), "%08X | %s| %s\n" % (pos, hexbytes, strbytes))
                pos = i
                hexbytes = ''
                strbytes = ''

        if i % 16 != 0:
            self.view.insert(self.edit, self.view.size(), "%08X | %-48s| %s" % (pos, hexbytes, strbytes))
        self.view.set_read_only(True)


class ViewAsTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.set_read_only(False)
        view = self.view
        fname = view.file_name()
        reg = sublime.Region(0, view.size())
        view.erase(edit, reg)
        f = open(fname, 'r')
        sfile = f.read()
        f.close()
        view.insert(edit, 0, sfile)


class ViewAsHexCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        hexed = HexEditor(edit)
        hexed.load_file()


class HexEditorListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        row, col = view.rowcol(view.sel()[0].b)
        sublime.status_message('[Row: %d, Col: %d]' % (row, col))
