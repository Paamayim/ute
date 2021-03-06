import urwid

from ute.gui import TimeEdit
from ute.gui.Catch import Catch
from ute.gui.CustomPalette import *
from ute.model import Data
from ute.model import DB
from ute.utils import *

TYPE_WIDTH = 16

def wrap(w, color = "field"):
    return urwid.AttrMap(w, color)

class Entry(urwid.WidgetWrap):
    _selectable = True

    def __init__(self, id = -1, msg = None, event = False):
        self.event = event
        self.id = id
        self.was_focused = False
        self.is_closed = False
        self.is_dirty = True

        defaults = (-2, "", "", -1, -1)
        if id != -1:
            defaults = Data.getInterval(id)

        if msg != None:
            defaults = (msg.id, msg.type, msg.desc, msg.open, msg.close)

        if defaults[0] != -2:
            if defaults[3] == defaults[4]:
                event = True
            if defaults[4] != None:
                self.is_closed = True

            if not (id > 0):
                self.is_dirty = False

        self.type_edit = urwid.Edit("", defaults[1])
        self.desc_edit = urwid.Edit("", defaults[2])
        self.start_edit = TimeEdit(defaults[3])
        self.end_edit = TimeEdit(defaults[4])

        end = None
        if not event and self.is_closed:
            end = wrap(self.end_edit)
        elif not self.is_closed and not self.event:
            end = urwid.Text(("open", "open"))
        else:
            end = urwid.Text("event")

        self.widget = urwid.Columns(
            [
                (TYPE_WIDTH, wrap(self.type_edit)),
                wrap(self.desc_edit),
                (7, wrap(self.start_edit)),
                (7, end),
                (1, Catch())
            ],
            dividechars = 1
        )
        urwid.WidgetWrap.__init__(self, self.widget)

        if not self.is_closed and event:
            self.doClose()

    @property
    def type(self):
        return self.type_edit.edit_text

    @property
    def desc(self):
        return self.desc_edit.edit_text

    @property
    def open(self):
        return self.start_edit.time

    @property
    def close(self):
        if self.event:
            return self.open
        if not self.is_closed:
            return None
        return self.end_edit.time


    def doClose(self):
        self.sync()

        if self.is_closed:
            return

        self.end_edit.fromTimestamp(now())
        if not self.event:
            self.widget.contents[3] = (
                wrap(self.end_edit),
                self.widget.options("given", 7))

        self.is_closed = True
        Data.closeInterval(self.id, self.close)


    def keypress(self, size, key):
        if key == "ctrl x":
            self.doClose()
            return None

        if "tab" in key:
            try:
                if "shift" in key:
                    self.widget.focus_col -= 1
                else:
                    self.widget.focus_col += 1
                return None
            except:
                pass

        self.is_dirty = True
        return self.widget.keypress(size, key)

    def refresh(self):
        color = "field"
        if self.type in type_mapping:
            color = type_mapping[self.type]
        self.widget.contents[0] = (
            wrap(self.type_edit, color),
            self.widget.options("given", TYPE_WIDTH))
        self.widget.contents[1] = (
            wrap(self.desc_edit, color),
            self.widget.options("weight", 1))




    def sync(self):
        self.id = Data.openInterval(
            self.id,
            self.type,
            self.desc,
            self.open,
            self.close
        )
        DB.commit()
        self.is_dirty = False

    def render(self, size, focus):
        if not focus and self.was_focused:
            self.sync()
        self.was_focused = focus

        toRender = self.widget
        if focus:
            toRender = urwid.AttrMap(toRender, "header")

        return toRender.render(size, focus)
