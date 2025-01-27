import os
from myutils.config import globalconfig, _TRL, static_data, getlanguse
from gui.usefulwidget import (
    getsimplecombobox,
    getcolorbutton,
    makegrid,
    tabadd_lazy,
    makescroll,
)


def setTablang(self):
    tabadd_lazy(self.tab_widget, ("语言设置"), lambda: setTablanglz(self))


def setTablangd(self):
    self.srclangswitcher = getsimplecombobox(
        _TRL(static_data["language_list_translator"]), globalconfig, "srclang3"
    )


def setTablanglz(self):
    grids = [
        [("翻译及OCR语言", 15)],
        [
            ("源语言", 5),
            (self.srclangswitcher, 5),
        ],
        [
            ("目标语言", 5),
            (
                getsimplecombobox(
                    _TRL(static_data["language_list_translator"]),
                    globalconfig,
                    "tgtlang3",
                ),
                5,
            ),
        ],
        [],
        [
            ("本软件显示语言(重启生效)", 5),
            (
                getsimplecombobox(
                    (static_data["language_list_show"]), globalconfig, "languageuse"
                ),
                5,
            ),
            (
                getcolorbutton(
                    globalconfig,
                    "",
                    callback=lambda: os.startfile(
                        os.path.abspath("./files/lang/{}.json".format(getlanguse()))
                    ),
                    icon="fa.gear",
                    constcolor="#FF69B4",
                ),
                1,
            ),
        ],
        [],
    ]

    gridlayoutwidget = makegrid(grids)
    gridlayoutwidget = makescroll(gridlayoutwidget)

    return gridlayoutwidget
