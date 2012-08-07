import sublime
import sublime_plugin


class HexEditor():
    def __init__(self, edit):
        self.edit = edit
        self.view = sublime.active_window().active_view()

    def load_file(self):
        self.view.erase(self.edit, sublime.Region(0, self.view.size()))
        with open(self.view.file_name(), 'rb') as f:
            bfile = f.read()

        i = pos = 0
        content = hexbytes = strbytes = ''

        for b in bfile:
            i += 1
            hexbytes += '%02X ' % ord(b)

            if b.isalnum():
                strbytes += b
            else:
                strbytes += '.'

            if i % 16 == 0:
                content += '%08X | %s| %s\n' % (pos, hexbytes, strbytes)
                # self.view.insert(self.edit, self.view.size(), content)
                pos = i
                hexbytes = strbytes = ''

        if i % 16 != 0:
            content += '%08X | %-48s| %s' % (pos, hexbytes, strbytes)
            # self.view.insert(self.edit, self.view.size(), content)

        self.view.insert(self.edit, 0, content)
        self.view.set_read_only(True)


class ViewAsTextCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        # Change mode to 'text'
        view.settings().set('mode', 'text')
        # Change syntax to previous
        view.settings().set('syntax', view.settings().get('original_syntax'))
        view.settings().set('is_syntax_changed', False)
        print 'Syntax changed to: ', view.settings().get('syntax')
        view.set_read_only(False)
        view.erase(edit, sublime.Region(0, view.size()))
        with open(view.file_name(), 'r') as f:
            sfile = f.read()
        view.insert(edit, 0, sfile)


class ViewAsHexCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        # Change mode to 'hex'
        view.settings().set('mode', 'hex')
        # Change syntax to Hex
        view.settings().set('syntax', 'Packages/Hex Tools/Hex.tmLanguage')
        view.settings().set('is_syntax_changed', False)
        print 'Syntax changed to: ', view.settings().get('syntax')
        # Set active area
        view.settings().set('area', 'text')
        hexed = HexEditor(edit)
        hexed.load_file()
        view.sel().clear()
        view.sel().add(sublime.Region(61, 61))
        view.sel().add(sublime.Region(11, 11))


class MoveCursorCommand(sublime_plugin.TextCommand):
    def run(self, edit, key=''):
        view = sublime.active_window().active_view()
        if view.settings().get('mode') == 'text':
            if key == 'left':
                view.run_command('move', {'by': 'characters', 'forward': False})
            elif key == 'right':
                view.run_command('move', {'by': 'characters', 'forward': True})
            elif key == 'up':
                view.run_command('move', {'by': 'lines', 'forward': False})
            elif key == 'down':
                view.run_command('move', {'by': 'lines', 'forward': True})
        elif view.settings().get('mode') == 'hex':
            if key == 'hex_area':
                self.view.settings().set('area', 'hex')
            elif key == 'text_area':
                self.view.settings().set('area', 'text')

            if not self.view.settings().has('area'):
                return

            current_point = view.sel()
            area = view.settings().get('area')
            sublime.status_message('Active area: %s' % area)
            if area == 'text':
                line, col = view.rowcol(current_point[1].b)
            else:
                line, col = view.rowcol(current_point[0].b)

            if key == 'left':
                if area == 'text':
                    if col == 61:
                        if line == 0:
                            col = 61
                        else:
                            line -= 1
                            col = 76
                    else:
                        col -= 1
                else:
                    if col == 11:
                        if line == 0:
                            col = 11
                        else:
                            line -= 1
                            col = 56
                    else:
                        col -= 3
            elif key == 'right':
                if area == 'text':
                    if col == 76:
                        line += 1
                        col = 61
                    else:
                        col += 1
                else:
                    if col == 56:
                        line += 1
                        col = 11
                    else:
                        col += 3
            elif key == 'up':
                if area == 'text':
                    if line != 0:
                        line -= 1
                else:
                    if line != 0:
                        line -= 1
            elif key == 'down':
                if area == 'text':
                    line += 1
                else:
                    line += 1

            view.sel().clear()
            pt1 = view.text_point(line, col)

            if area == 'text':
                pt2 = view.text_point(line, 11 + (col - 61) * 3)
                view.sel().add(sublime.Region(pt1 + 1, pt1))
                view.sel().add(sublime.Region(pt2 + 2, pt2))
            else:
                pt2 = view.text_point(line, 61 + (col - 11) / 3)
                view.sel().add(sublime.Region(pt2 + 1, pt2))
                view.sel().add(sublime.Region(pt1 + 2, pt1))


class InitViewSettings(sublime_plugin.EventListener):
    def on_load(self, view):
        # Set view mode
        if not view.settings().has('mode'):
            view.settings().set('mode', 'text')
        # Set original syntax
        if not view.settings().has('is_syntax_changed'):
            view.settings().set('is_syntax_changed', False)
        if not view.settings().has('original_syntax'):
            view.settings().set('original_syntax', view.settings().get('syntax'))
