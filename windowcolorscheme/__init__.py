import configparser
import os
import subprocess
import time

from Xlib import display, X
from PIL import Image


# TODO: Unhardcode this
default_config = configparser.ConfigParser()
default_config.optionxform = str
with open(os.environ['HOME'] + f'/.local/share/color-schemes/AritimDark.colors', 'r') as f:
    default_config.read_file(f)

cached_data = dict()


def reload_config():
    # wasn't able to send signal via python-dbus, thus why this code exist
    subprocess.check_call([
        'dbus-send',
        '--type=signal',
        '--dest=org.kde.KWin',
        '/KWin',
        'org.kde.KWin.reloadConfig'
    ])


def get_foreground(background: str):
    r, g, b = [float(i) for i in background.split(',')]
    lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return '255,255,255' if lum < 0.5 else '0,0,0'


def set_window_config(window_class, name, color):
    if cached_data.get(name) == color:
        return False
    cached_data[name] = color

    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(os.environ['HOME'] + '/.config/kwinrulesrc')
    window_section = None
    for section in config.sections():
        if section == 'General':
            continue
        description = config.get(section, 'Description')
        if description == 'windowcolorscheme_' + name:
            window_section = section
            break

    is_fresh_rule = False
    if window_section is None:
        is_fresh_rule = True
        count = str(int(config.get('General', 'count')) + 1)
        config.set('General', 'count', count)
        window_section = count
        config.add_section(count)
        config.set(window_section, 'Description', 'windowcolorscheme_' + name)
        config.set(window_section, 'clientmachine', 'localhost')
        config.set(window_section, 'clientmachinematch', '0')
        config.set(window_section, 'decocolor', 'windowcolorscheme_' + name)
        config.set(window_section, 'decocolorrule', '2')
        config.set(window_section, 'wmclass', window_class)
        config.set(window_section, 'wmclasscomplete', 'true')
        config.set(window_section, 'wmclassmatch', '1')

    scheme = default_config
    # scheme.optionxform = str
    if not scheme.has_section('General'):
        scheme.add_section('General')
    if not scheme.has_section('WM'):
        scheme.add_section('WM')
    if not scheme.has_section('Colors:Window'):
        scheme.add_section('Colors:Window')
    scheme.set('General', 'Name', 'windowcolorscheme_' + name)
    scheme.set('WM', 'activeBackground', color)
    scheme.set('WM', 'activeForeground', get_foreground(color))
    scheme.set('Colors:Window', 'BackgroundNormal', color)
    with open(
            os.environ['HOME'] + f'/.local/share/color-schemes/windowcolorscheme_{name}.colors',
            'w'
    ) as f:
        scheme.write(f, space_around_delimiters=False)

    if is_fresh_rule or config.get(window_section, 'decocolor') != 'windowcolorscheme_' + name:
        config.set(window_section, 'decocolor', 'windowcolorscheme_' + name)
        with open(os.environ['HOME'] + '/.config/kwinrulesrc', 'w') as f:
            config.write(f, space_around_delimiters=False)
        reload_config()

    return True


display = display.Display()
root = display.screen().root

NET_ACTIVE_WINDOW = display.intern_atom('_NET_ACTIVE_WINDOW')
WM_CLASS = display.intern_atom('WM_CLASS')
NET_WM_NAME = display.intern_atom('_NET_WM_NAME')
NET_WM_PID = display.intern_atom('_NET_WM_PID')
NET_WM_STATE = display.intern_atom('_NET_WM_STATE')

last_seen = {'xid': None}


def get_active_window():
    window_id = root.get_full_property(NET_ACTIVE_WINDOW,
                                       X.AnyPropertyType).value[0]

    focus_changed = (window_id != last_seen['xid'])
    last_seen['xid'] = window_id

    return display.create_resource_object('window', window_id), focus_changed


def main():
    root.change_attributes(event_mask=X.PropertyChangeMask)
    is_bad_window = False
    while True:
        win, changed = get_active_window()
        if not is_bad_window or changed:
            try:
                # TODO: Application/window -specific detection configuration
                is_bad_window = False
                win.map()
                width = win.get_geometry().width
                height = 1
                raw = win.get_image(0, 1, width, height, X.ZPixmap, 0xffffffff)
                image = Image.frombytes('RGB', (width, height), raw.data, 'raw', 'BGRX')
                colors = image.getcolors()
                if colors is None:
                    target_color = (0, 0, 0)
                else:
                    target_color = sorted(colors, key=lambda k: k[0])[-1][1]

                wm_class = ' '.join(win.get_wm_class())
                name = '_'.join(win.get_wm_class())

                set_window_config(wm_class, name, ','.join(map(str, target_color)))
            except Exception as e:
                print(e)
                is_bad_window = True

        while display.pending_events():
            event = display.next_event()
        time.sleep(1 / 60)


if __name__ == '__main__':
    main()
