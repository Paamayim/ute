import urwid


class TimeEdit(urwid.WidgetWrap):
    def __init__(self):
        self.widget = urwid.Edit("", "12:34")
        urwid.WidgetWrap.__init__(self, self.widget)

    def render(self, size, focus):
        if self.widget.edit_pos > 4:
            self.widget.edit_pos = 4

        toRender = self.widget
        result = self.widget.render(size, focus)
        return result

    def keypress(self, size, key):
        allowed = map(lambda x: str(x), range(0, 10))

        handled = []
        handled.extend(allowed)
        handled.extend(["left", "right", "delete", "backspace"])

        if key not in handled:
            return key

        if key in allowed:
            self.widget.keypress(size, "delete")

        result = self.widget.keypress(size, key)

        self.validate()

        if self.widget.edit_pos == 2:
            if key in ["left", "backspace"]:
                self.widget.edit_pos -= 1
            else:
                self.widget.edit_pos += 1
        if self.widget.edit_pos > 4:
            return "right"
        return result

    def mouse_event(self, size, event, button, x, y, focus):
        result = self.widget.mouse_event(size, event, button, x, y, focus)
        if self.pos == 2:
            self.pos = 3
        return result

    @property
    def text(self):
        return self.widget.edit_text

    @text.setter
    def text(self, value):
        self.widget.edit_text = value

    @property
    def pos(self):
        return self.widget.edit_pos

    @pos.setter
    def pos(self, value):
        self.widget.edit_pos = value

    def validate(self):
        def clamp(val, bot, top):
            return max(bot, min(val, top))

        h = int(self.text[0:2])
        m = int(self.text[3:5])
        if not (0 < h and h < 24 and 0 < m and m < 60):
            h = clamp(h, 0, 23)
            m = clamp(m, 0, 59)
            self.text = '{:0^2}:{:0^2}'.format(h, m)

