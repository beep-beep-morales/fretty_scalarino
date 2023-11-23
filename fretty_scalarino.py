#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2023 Blackthorn CBG, BlackthornCBG@gmail.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

"""
A simple utility to draw fretboard templates for Cigar Box Guitars
"""

import inkex


class FrettyScalarino(inkex.EffectExtension):
    def add_arguments(self, pars):
        """Parses the arguments defined in the INX file"""
        pars.add_argument("--template_width", type=float, default="1.50")
        pars.add_argument("--page_margin", type=float, default="0.50")
        pars.add_argument("--scale_length", type=float, default="25.00")
        pars.add_argument("--number_of_frets", type=int, default="20")
        pars.add_argument("--fret_slot_width", type=float, default="0.023in")
        pars.add_argument("--nut_length", type=float, default="0.20")
        pars.add_argument("--nut_position", default="leading_edge")
        pars.add_argument("--fret_markers", default="true")

    def assign_variables(self):
        """Assigns the variables parsed from the INX file to instance variables"""
        self.current_layer = self.svg.get_current_layer()

        self.template_width_inches = self.options.template_width
        self.template_width_uu = self.current_layer.unittouu(
            str(self.template_width_inches) + "in"
        )

        self.page_margin_inches = self.options.page_margin
        self.page_margin_uu = self.current_layer.unittouu(
            str(self.page_margin_inches) + "in"
        )

        self.scale_length_inches = self.options.scale_length
        self.scale_length_uu = self.current_layer.unittouu(
            str(self.scale_length_inches) + "in"
        )

        self.fret_slot_width = str(self.options.fret_slot_width) + "in"
        self.fret_slot_width = self.current_layer.unittouu(self.fret_slot_width)

        self.number_of_frets = self.options.number_of_frets

        self.nut_length_inches = self.options.nut_length
        self.nut_length_uu = self.current_layer.unittouu(
            str(self.nut_length_inches) + "in"
        )

        self.nut_position_uu = self.nut_length_uu / 2 + self.page_margin_uu
        self.nut_offset_inches = 0
        if self.options.nut_position == "leading_edge":
            self.nut_offset_inches = self.nut_length_inches
        else:
            self.nut_offset_inches = self.nut_length_inches / 2

        self.fret_markers = self.options.fret_markers

        self.document_width = self.svg.viewport_width
        self.document_width_uu = self.current_layer.unittouu(self.document_width)
        self.docuemnt_width_inches = inkex.units.convert_unit(
            str(self.document_width), "in"
        )
        self.document_width_usable = self.document_width_uu - self.page_margin_uu * 2

        self.document_height = self.svg.viewport_height
        self.document_height_uu = self.current_layer.unittouu(self.document_height)
        self.document_height_inches = inkex.units.convert_unit(
            str(self.document_height), "in"
        )
        self.document_height_usable = self.document_height_uu - self.page_margin_uu * 2

    def add_text(self, x_uu, y_uu, text):
        """Add a text label at the given x,y location."""
        element = inkex.TextElement(x=str(x_uu), y=str(y_uu))
        element.text = str(text)
        element.style = {
            "font-size": self.svg.unittouu("8pt"),
            "fill-opacity": "1.0",
            "stroke": "none",
            "font-weight": "bold",
            "font-style": "normal",
        }
        return element

    def fret_distance_from_nut(self, fret):
        """Calculate the distance from the guitar nut in inches for a given fret number, based on the scale length parameter.
        Does not account for the length of the nut, or if the distance is calculated from the center of the nut or the leading edge.
        """
        return self.scale_length_inches - self.scale_length_inches / pow(
            2.0, (fret / 12.0)
        )

    def sort_and_draw_frets(self, fret_number):
        fret_list = list(range(1, fret_number + 1))
        offset = 0
        self.columns = 0
        reset_page_top = False
        fret_distance_from_page_top_inches = 0 + self.page_margin_inches
        limit_inches = self.document_height_inches - self.page_margin_inches

        while len(fret_list) > 0:
            fret = fret_list.pop(0)
            fret_distance_from_previous_fret_inches = round(
                (self.fret_distance_from_nut(fret))
                - (self.fret_distance_from_nut(fret - 1)),
                3,
            )
            fret_distance_from_previous_fret_uu = self.current_layer.unittouu(
                str(fret_distance_from_previous_fret_inches) + "in"
            )
            fret_distance_from_page_top_inches = round(
                fret_distance_from_page_top_inches
                + fret_distance_from_previous_fret_inches,
                3,
            )

            # we need to account for the page margin and the length of the nut when drawing the first fret
            if self.columns == 0 and fret == 1:
                fret_distance_from_page_top_inches = (
                    fret_distance_from_page_top_inches + self.nut_offset_inches
                )

            if reset_page_top == True:
                fret_distance_from_page_top_inches = 0.25 + self.page_margin_inches
                reset_page_top = False
            else:
                pass
                # fret_distance_from_page_top = fret_distance_from_page_top + fret_distance_from_previous_fret

            distance_from_limit = round(
                (limit_inches - (fret_distance_from_page_top_inches % limit_inches)), 3
            )

            if fret_distance_from_page_top_inches > limit_inches:
                offset = offset + limit_inches
                fret_list.insert(0, fret)
                fret_list.insert(0, fret - 1)
                self.columns = self.columns + 1
                reset_page_top = True
                continue

            fret_distance_from_page_top_uu = self.current_layer.unittouu(
                str(fret_distance_from_page_top_inches) + "in"
            )

            self.draw_fret(fret, self.columns, fret_distance_from_page_top_uu)

            if self.fret_markers == "true":
                if fret in [3, 5, 7, 9, 12, 15, 17, 19, 21, 24]:
                    marker_distance = fret_distance_from_page_top_uu - (
                        fret_distance_from_previous_fret_uu / 2
                    )
                    self.draw_fret_marker(fret, self.columns, marker_distance)

            # Store the position of the final fret to make drawing the borders of the fretboard easier
            if fret == fret_number:
                self.final_fret_position_uu = fret_distance_from_page_top_uu

    def draw_fret(self, fret, column, distance):
        x1 = (
            column * self.template_width_uu
            + self.page_margin_uu
            + column * self.current_layer.unittouu("0.4 in")
        )
        x2 = x1 + self.template_width_uu

        fret_line = self.current_layer.add(
            inkex.Line.new(
                f"{x1},{distance}",
                f"{x2},{distance}",
            )
        )
        fret_line.style["stroke"] = "#000000"
        fret_line.style["stroke-width"] = f"{self.fret_slot_width}"
        self.current_layer.add(
            self.add_text(
                x1 + self.template_width_uu / 4,
                distance - 1,
                f"Fret #{fret}",
            )
        )

    def draw_cross(self, x, y):
        horizontal_line = self.current_layer.add(
            inkex.Line.new(
                f"{x-2},{y}",
                f"{x+2},{y}",
            )
        )
        horizontal_line.style["stroke"] = "#000000"
        horizontal_line.style["stroke-width"] = f"{self.fret_slot_width}"

        vertical_line = self.current_layer.add(
            inkex.Line.new(
                f"{x},{y-2}",
                f"{x},{y+2}",
            )
        )
        vertical_line.style["stroke"] = "#000000"
        vertical_line.style["stroke-width"] = f"{self.fret_slot_width}"

    def draw_fret_marker(self, fret, column, distance):
        x_left = (
            column * self.template_width_uu
            + self.page_margin_uu
            + column * self.current_layer.unittouu("0.4 in")
        )
        x = x_left + self.template_width_uu / 2
        y = distance
        if distance > self.page_margin_uu:
            if fret in [12, 24]:
                marker_offset = self.template_width_uu / 4
                self.draw_cross(x - marker_offset, y)
                self.draw_cross(x + marker_offset, y)
            else:
                self.draw_cross(x, y)

    def draw_nut(self):
        """Draw the guitar nut using the nut length specified in the UI. Inkscape draws lines centered on their cooridinates,
        so nut position is calculated at 1/2 the nut length"""
        nut_line = self.current_layer.add(
            inkex.Line.new(
                f"{self.page_margin_uu},{self.nut_position_uu}",
                f"{self.page_margin_uu+self.template_width_uu},{self.nut_position_uu}",
            )
        )
        nut_line.style["stroke"] = "#000000"
        nut_line.style["stroke-width"] = f"{self.nut_length_uu}"

    def draw_template_border(self):
        count = 0
        draw_bottom = False
        while count <= self.columns:
            x1 = (
                count * self.template_width_uu
                + self.page_margin_uu
                + count * self.current_layer.unittouu("0.4 in")
            )
            x2 = x1 + self.template_width_uu
            y1 = self.page_margin_uu
            if count == self.columns:
                draw_bottom = True
                y2 = self.final_fret_position_uu
            else:
                y2 = self.document_height_uu - self.page_margin_uu

            fretboard_border_left = self.current_layer.add(
                inkex.Line.new(
                    f"{x1},{y1}",
                    f"{x1},{y2}",
                )
            )
            fretboard_border_left.style["stroke"] = "#000000"
            fretboard_border_left.style["stroke-width"] = f"{self.fret_slot_width}"

            fretboard_border_right = self.current_layer.add(
                inkex.Line.new(
                    f"{x2},{y1}",
                    f"{x2},{y2}",
                )
            )
            fretboard_border_right.style["stroke"] = "#000000"
            fretboard_border_right.style["stroke-width"] = f"{self.fret_slot_width}"

            if draw_bottom == True:
                fretboard_border_bottom = self.current_layer.add(
                    inkex.Line.new(
                        f"{x1},{y2}",
                        f"{x2},{y2}",
                    )
                )
                fretboard_border_bottom.style["stroke"] = "#000000"
                fretboard_border_bottom.style[
                    "stroke-width"
                ] = f"{self.fret_slot_width}"

            count = count + 1

    def draw_page_border(self):
        page_border = self.current_layer.add(
            inkex.Rectangle.new(
                self.page_margin_uu,
                self.page_margin_uu,
                self.document_width_usable,
                self.document_height_usable,
            )
        )
        page_border.style["stroke"] = "#c8c8c8"
        page_border.style["stroke-width"] = f"{self.fret_slot_width}"
        page_border.style["fill"] = "none"

    def effect(self):
        """This functinon is executed automatically when the extension is applied"""
        self.assign_variables()
        self.draw_nut()
        self.draw_page_border()
        self.sort_and_draw_frets(self.number_of_frets)
        self.draw_template_border()


if __name__ == "__main__":
    FrettyScalarino().run()
