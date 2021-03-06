﻿# Copyright 2004-2016 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

init python:
    import gui7
    import os

    from store import config

    for fn in [ "gui.rpy", "options.rpy", "script.rpy" ]:
        fn = os.path.join(config.renpy_base, "gui", "game", fn)
        if os.path.exists(fn):
            config.translate_files.append(fn)

    config.translate_comments = config.translate_files


    COLORS = [
        "#0099cc",
        "#99ccff",
        "#66cc00",
        "#cccc00",
        "#cc6600",
        # "#cc3300",

        "#0066cc",
        "#9933ff",
        "#00cc99",
        "#cc0066",
        "#cc0000",
    ]

    COLOR_OPTIONS = [
        (i, "#000000", False) for i in COLORS
    ] + [
        (i, "#ffffff", True) for i in COLORS
    ]


#     LIGHT_COLORS = [
#         "#cc6600",
#         "#0099ff",
#         "#cc0066",
#         "#990000",
#         "#000000",
#         "#003366",
#         "#006666",
#         "#000066",
#         "#660066",
#         "#336600",
#     ]


screen gui_swatches():

    grid 5 4:

        for accent, bg, light in COLOR_OPTIONS:

            frame:
                style "empty"
                xysize (85, 60)

                add Color(accent).replace_hsv_saturation(.25).replace_value(.5)
                add Color(bg).opacity(.8)

                button:
                    style "empty"

                    if light:
                        selected_background "#000"
                    else:
                        selected_background "#fff"

                    xpadding 3
                    ypadding 3
                    xmargin 10
                    ymargin 10

                    action SetVariable("gui_color", (accent, bg, light))

                    idle_child Solid(accent)
                    hover_child Solid(Color(accent).tint(.6))

screen gui_demo(accent, boring, light, display):

    $ p = gui7.GuiParameters(
        "-",
        "-",
        1280,
        720,
        accent,
        boring,
        light,
        None,
        False,
        False,
        False,
        "-"
    )

    frame:
        style "empty"

        add p.menu_color
        add Solid(p.boring_color.opacity(.8))

        frame:
            style "empty"

            xpadding 10
            ypadding 10

            has vbox

            text _("Display"):
                style "empty"
                # font "DejaVuSans.ttf"
                color p.accent_color
                size 24

            for i in [ _("Window"), _("Fullscreen"), _("Planetarium") ]:

                textbutton i:
                    action SetScreenVariable("display", i)
                    style "empty"

                    text_style "empty"
                    text_size 24

                    text_color p.idle_color
                    text_hover_color p.hover_color
                    text_selected_color p.selected_color

                    xmargin 4
                    ymargin 4
                    left_padding 21

                    selected_background Solid(p.accent_color, xsize=5)

            null height 30

            text _("Text Speed"):
                style "empty"
                color p.accent_color
                size 24

            bar:
                value ScreenVariableValue("value", 1.0)
                style "empty"
                base_bar Solid(p.muted_color)
                hover_base_bar Solid(p.hover_muted_color)

                thumb Solid(p.accent_color, xsize=10)
                hover_thumb Solid(p.hover_color, xsize=10)

                ysize 30


screen choose_gui_color():

    default display = "Window"
    default value = 0.5

    frame:
        style_group "l"
        style "l_root"

        window:
            has vbox

            label _("Select Accent and Background Colors")

            frame:
                style "l_indent"

                has hbox:
                    yfill True

                frame:
                    style "l_default"
                    xsize 350

                    has vbox

                    text _("Please click on the color scheme you wish to use, then click Continue. These colors can be changed and customized later.")

                    add SPACER

                    use gui_swatches()


                # Preview
                frame:
                    style "l_default"
                    background Frame(PATTERN, 0, 0, tile=True)
                    xpadding 5
                    ypadding 5

                    xfill True
                    yfill True
                    xmargin 20
                    bottom_margin 6

                    use gui_demo(gui_color[0], gui_color[1], gui_color[2], display)

    textbutton _("Back") action Jump("front_page") style "l_left_button"

    if gui_color:
        textbutton _("Continue") action Return(True) style "l_right_button"


label change_gui:

    python:

        gui_new = False
        gui_replace_images = True
        gui_update_code = True

        project.current.update_dump(True)
        gui_size = tuple(project.current.dump["size"])

        gui_replace_code = interface.choice(
            _("{b}Warning:{/b} Both choices will overwrite all gui image files, except for main_menu.png, game_menu.png, and window_icon.png.\n\nUpdating gui.rpy will {b}destroy{/b} any changes you have made to gui.rpy.\n\nWhat would you like to do?"),
            [
                (False, _("Change gui colors.")),
                (True, _("Update gui.rpy to the latest version, changing sizes and colors.")),
            ],
            False,
            cancel=Jump("front_page"),
        )

        project_dir = project.current.path
        project_name = project.current.name

    if gui_replace_code:
        jump gui_project_size
    else:
        jump gui_project_common

label new_gui_project:

    python:
        gui_new = True

        project_name = interface.input(
            _("PROJECT NAME"),
            _("Please enter the name of your project:"),
            filename=True,
            cancel=Jump("front_page"))

        project_name = project_name.strip()
        if not project_name:
            interface.error(_("The project name may not be empty."))

        project_dir = os.path.join(persistent.projects_directory, project_name)

        if project.manager.get(project_name) is not None:
            interface.error(_("[project_name!q] already exists. Please choose a different project name."), project_name=project_name)

        if os.path.exists(project_dir):
            interface.error(_("[project_dir!q] already exists. Please choose a different project name."), project_dir=project_dir)

        gui_replace_images = True
        gui_replace_code = True
        gui_update_code = True


label gui_project_size:

    python:

        gui_size = interface.choice(
            _("What resolution should the project use? Although Ren'Py can scale the window up and down, this is the initial size of the window, the size at which assets should be drawn, and the size at which the assets will be at their sharpest.\n\nThe default of 1280x720 is a reasonable compromise."),
            [
                ((1066, 600), "1066x600"),
                ((1280, 720), "1280x720"),
                ((1920, 1080), "1920x1080"),
            ],
            (1280, 720),
            cancel=Jump("front_page"),
        )

label gui_project_common:

    $ gui_color = (COLORS[0], "#000000", False)

    call screen choose_gui_color

    python hide:

        width, height = gui_size
        accent, boring, light = gui_color

        prefix = os.path.join(project_dir, "game")

        if not os.path.isdir(prefix) and not gui_new:
            interface.error("{} does not appear to be a Ren'Py game.".format(prefix))

        template = os.path.join(config.renpy_base, "gui", "game")

        if not os.path.isdir(template):
            interface.error("{} does not appear to be a Ren'Py game.".format(template))

        p = gui7.GuiParameters(
            prefix,
            template,
            width,
            height,
            accent,
            boring,
            light,
            _preferences.language,
            gui_replace_images,
            gui_replace_code,
            gui_update_code,
            project_name,
            )

        if gui_new:
            interface.processing(_("Creating the new project..."))
        else:
            interface.processing(_("Updating the project..."))

        with interface.error_handling("creating a new project"):
            gui7.generate_gui(p)

        # Activate the project.
        with interface.error_handling("activating the new project"):
            project.manager.scan()
            project.Select(project.manager.get(project_name))()

    jump front_page
