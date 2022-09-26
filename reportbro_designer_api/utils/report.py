# -*- coding: utf-8 -*-
"""
@create: 2020-05-07 09:21:47.

@author: jzd

@desc: RporetPdf 生成类
"""
import datetime
import glob
import os
import re
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from typing import List

from reportbro import Report
from reportbro.reportbro import DocumentPDFRenderer
from reportbro.reportbro import DocumentXLSXRenderer

FONT_TYPES = {
    "bold": "bold_filename",
    "bolder": "bold_filename",
    "b": "bold_filename",
    "light": "light_filename",
    "lighter": "light_filename",
    "l": "light_filename",
    "normal": "filename",
    "regular": "filename",
    "r": "filename",
    "n": "filename",
}


def fill_default(report_definition, data):
    """Input data padding default."""
    parameters = report_definition["parameters"]

    def _loop_params(_parameters):
        for i in _parameters:
            if i["showOnlyNameType"]:
                continue

            yield i

    def _fill_default(_parame, _data):
        _type = _parame["type"]
        _name = _parame["name"]

        if _data.get(_name, None):
            if _type == "map":
                for ppp in _loop_params(_parame["children"]):
                    _fill_default(ppp, _data[_name])
            elif _type == "array":
                for ppp in _loop_params(_parame["children"]):
                    for data in _data[_name]:
                        _fill_default(ppp, data)
            return

        if _type == "number":
            _data[_name] = 0.00
        elif _type == "string":
            _data[_name] = ""
        elif _type == "boolean":
            _data[_name] = False
        elif _type == "date":
            _data[_name] = "1900-01-01"
        elif _type in ["simple_array", "array"]:
            _data[_name] = []
        elif _type == "image":
            _data[_name] = ""
        elif _type == "map":
            _data[_name] = {}
            for ppp in _parame["children"]:
                _fill_default(ppp, _data[_name])

    for i in _loop_params(parameters):
        _fill_default(i, data)


@dataclass
class ReportFonts(object):
    """ReportFonts."""

    value: str = ""
    filename: str = ""
    bold_filename: str = ""
    light_filename: str = ""

    def to_jinja2(self):
        """to_jinja2."""
        if self.filename:
            self.filename = self.filename

        return {
            "name": self.value,
            "href": os.path.basename(self.filename),
        }


class ReportFontsLoader(object):
    """ReportFontsLoader."""

    LOAD_FMT_REGIX = re.compile(
        r"^(?:[0-9].*?-)*(.*?)(?:-[0-9]*?)*-"
        r"(bold|bolder|lighter|light|normal|medium|regular|N|M|R|L|B)\.(otf|ttf)$",
        re.MULTILINE | re.IGNORECASE,
    )

    def __init__(self, font_path: str):
        """__init__."""
        self.fonts_cls: List[ReportFonts] = []
        self.fonts = []
        self.font_path = font_path
        self.load()

    def load(self):
        """Load fonts in path."""
        path_list = defaultdict(list)
        for path in glob.glob(self.font_path + "/*.ttf"):
            dirname = os.path.basename(path)
            names = self.LOAD_FMT_REGIX.match(dirname)
            if not names:
                continue

            names = names.groups()
            path_list[names[0]].append((path, names))

        fonts = []
        for name, paths in path_list.items():
            paths_map = {"value": name}
            for i in paths:
                key = FONT_TYPES.get(i[1][1].lower(), None)
                if not key:
                    continue

                paths_map[key] = i[0]

                if "filename" not in paths_map:
                    paths_map["filename"] = i[0]

            if len(paths_map) > 1:
                fonts.append(ReportFonts(**paths_map))

        self.fonts_cls = fonts
        self.fonts_jinja = [i.to_jinja2() for i in fonts]
        self.fonts = [asdict(i) for i in fonts]


class ReportPdf(object):
    """ReportPdf."""

    def __init__(
        self,
        report_definition,
        data,
        font_loader: ReportFontsLoader,
        is_test_data=False,
        **kwargs
    ):
        """__init__."""
        self.font_loader = font_loader
        self.report = Report(
            report_definition,
            data,
            is_test_data,
            additional_fonts=font_loader.fonts,
            **kwargs,
        )

    def generate_pdf(self, filename="", add_watermark=False, title=""):
        """generate_pdf."""
        renderer = DocumentPDFRenderer(
            header_band=self.report.header,
            content_band=self.report.content,
            footer_band=self.report.footer,
            report=self.report,
            context=self.report.context,
            additional_fonts=self.report.additional_fonts,
            filename=filename,
            add_watermark=add_watermark,
            page_limit=self.report.page_limit,
            encode_error_handling="ignore",
            core_fonts_encoding="utf8",
        )
        if title:
            renderer.pdf_doc.set_title(
                "_".join([title, datetime.datetime.now().strftime("%Y%m%dT%H%M%S")])
            )

        return renderer.render()

    def generate_xlsx(self, filename=""):
        """generate_xlsx."""
        renderer = DocumentXLSXRenderer(
            header_band=self.report.header,
            content_band=self.report.content,
            footer_band=self.report.footer,
            report=self.report,
            context=self.report.context,
            filename=filename,
        )
        return renderer.render()
