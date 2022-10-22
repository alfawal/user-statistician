# user-statistician: Github action for generating a user stats card
#
# Copyright (c) 2021-2022 Vincent A Cicirello
# https://www.cicirello.org/
#
# MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import copy
import json
import unittest

from src.Colors import *
from src.ColorUtil import (
    _namedColors,
    contrastRatio,
    highContrastingColor,
    isValidColor,
)
from src.StatConfig import *
from src.Statistician import *
from src.StatsImageGenerator import StatsImageGenerator
from src.TextLength import *
from src.UserStatistician import writeImageToFile

# Set to True to cause tests to generate a sample SVG, or False not to.
outputSampleSVG = False
localeCode = "en"

with open("tests/test_seed.json", "r") as f:
    data = json.load(f)
    executedQueryResultsOriginal = data["executedQueryResultsOriginal"]
    executedQueryResultsMultiPage = data["executedQueryResultsMultiPage"]


class TestSomething(unittest.TestCase):
    def test_parseQueryResults(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsOriginal)

        class NoQueries(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueries(True, False, 1000, set(), None)
        self._validate(stats)

    def test_parseQueryResultsMultiPage(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsMultiPage)

        class NoQueries(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueries(True, False, 1000, set(), None)
        self._validate(stats)

    def test_parseQueryResultsSkipRepo(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsOriginal)

        class NoQueriesMultipage(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueriesMultipage(
            True, False, 1000, {"repo29", "repoDoesntExist"}, None
        )
        self._validate(stats, True)

    def test_parseQueryResultsMultipageSkipRepo(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsMultiPage)

        class NoQueriesMultipage(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueriesMultipage(
            True, False, 1000, {"repo29", "repoDoesntExist"}, None
        )
        self._validate(stats, True)

    def test_parseQueryResultsAllForks(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsOriginal)
        # Change all repos to forks for this testcase.
        self._changeToAllForks(executedQueryResults)

        class NoQueries(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueries(True, False, 1000, set(), None)
        self._validateAllForks(stats)

    def test_color_themes(self):
        originalThemes = {
            "batty",
            "light",
            "light-colorblind",
            "light-high-contrast",
            "light-tritanopia",
            "dark",
            "dark-colorblind",
            "dark-dimmed",
            "dark-high-contrast",
            "dark-tritanopia",
            "halloween",
            "halloween-light",
        }
        for theme in originalThemes:
            self._colorValidation(colorMapping[theme])
            self._iconValidation(colorMapping[theme])
        for theme in colorMapping:
            if theme not in originalThemes:
                self._colorValidation(colorMapping[theme])
                self._iconValidation(colorMapping[theme])

    def test_color_contrast_text_vs_bg(self):
        for theme, colors in colorMapping.items():
            crText = contrastRatio(colors["bg"], colors["text"])
            crTitle = contrastRatio(colors["bg"], colors["title"])
            self.assertTrue(crText >= 4.5, msg=theme + " " + str(crText))
            self.assertTrue(crTitle >= 4.5, msg=theme + " " + str(crTitle))

    def test_title_templates(self):
        unlikelyInTemplate = "qwertyuiop"
        try:
            for locale in supportedLocales:
                title = titleTemplates[locale].format(unlikelyInTemplate)
                self.assertTrue(
                    titleTemplates[locale].find("{0}") < 0
                    or title.find(unlikelyInTemplate) >= 0
                )
        except IndexError:
            self.fail()

    def test_categories(self):
        categories = {"general", "repositories", "contributions", "languages"}
        self.assertEqual(set(categoryOrder), categories)
        statistics = {
            "joined",
            "featured",
            "mostStarred",
            "mostForked",
            "followers",
            "following",
            "sponsors",
            "sponsoring",
            "public",
            "starredBy",
            "forkedBy",
            "watchedBy",
            "templates",
            "archived",
            "commits",
            "issues",
            "prs",
            "reviews",
            "contribTo",
            "private",
        }

        # Make sure all are accounted for in a category
        statKeys = {stat for cat in categoryOrder for stat in statsByCategory[cat]}
        self.assertEqual(statistics, statKeys)

        # Make sure none are in more than one categories
        numStats = sum(len(statsByCategory[cat]) for cat in categoryOrder)
        self.assertEqual(numStats, len(statistics))

    def test_category_labels(self):
        categories = categoryOrder
        types = {"heading", "column-one", "column-two"}
        for locale in supportedLocales:
            self.assertTrue(locale in categoryLabels)
            labelMap = categoryLabels[locale]
            for cat in categories:
                self.assertTrue(cat in labelMap)
                for t in types:
                    self.assertTrue(t in labelMap[cat])

    def test_stat_labels(self):
        keys = {
            "joined",
            "featured",
            "mostStarred",
            "mostForked",
            "followers",
            "following",
            "sponsors",
            "sponsoring",
            "public",
            "starredBy",
            "forkedBy",
            "watchedBy",
            "templates",
            "archived",
            "commits",
            "issues",
            "prs",
            "reviews",
            "contribTo",
            "private",
        }
        self.assertTrue(all(k in statLabels for k in keys))
        for k in keys:
            self.assertTrue("icon" in statLabels[k])
            self.assertTrue(statLabels[k]["icon"].startswith("<path "))
            self.assertTrue(statLabels[k]["icon"].endswith("/>"))
            labelsByLocale = statLabels[k]["label"]
            for locale in supportedLocales:
                self.assertTrue(locale in labelsByLocale)

    def test_isValidColor(self):
        for colorName, colorHex in _namedColors.items():
            self.assertTrue(isValidColor(colorHex))
            self.assertTrue(isValidColor(colorName))

    def test_highContrastingColor(self):
        # Not really a good way to test this in an automated way.
        # This test method generates an SVG, outputted to standard out
        # with one rectangle for each named color and the name of the color
        # in the computed high contrasting color in text.
        # Uncomment the print statement to view results.
        # One time test. Only rerun if code of highContrastingColor
        # is changed.
        rows = [
            """<svg width="130" height="{0}" viewBox="0 0 130 {0}" xmlns="http://www.w3.org/2000/svg">""".format(
                str(len(_namedColors) * 20)
            )
        ]
        templateRect = """<rect width="130" height="20" fill="{0}" x="0" y="{1}" />"""
        templateText = """<text font-size="14" x="15" y="{2}" fill="{1}">{0}</text>"""
        y = 0
        for c in _namedColors:
            rows.append(templateRect.format(c, str(y)))
            rows.append(templateText.format(c, highContrastingColor(c), str(y + 12.5)))
            y += 20
        rows.append("</svg>")
        # Uncomment me and pipe to colorTest.svg
        # print("\n".join(rows))

    def test_TextLength(self):
        # We have known text lengths of "coverage" and "branches"
        # from another project, so using these as test cases.
        self.assertEqual(510, calculateTextLength110("coverage"))
        self.assertEqual(507, calculateTextLength110("branches"))
        self.assertAlmostEqual(51.0, calculateTextLength("coverage", 11, False, 400))
        self.assertAlmostEqual(50.7, calculateTextLength("branches", 11, False, 400))
        self.assertAlmostEqual(
            510, calculateTextLength("coverage", 146 + 2 / 3, True, 400)
        )
        self.assertAlmostEqual(
            507, calculateTextLength("branches", 146 + 2 / 3, True, 400)
        )
        self.assertAlmostEqual(
            51.0, calculateTextLength("coverage", 14 + 2 / 3, True, 400)
        )
        self.assertAlmostEqual(
            50.7, calculateTextLength("branches", 14 + 2 / 3, True, 400)
        )
        self.assertAlmostEqual(76.5, calculateTextLength("coverage", 11, False, 600))
        self.assertAlmostEqual(76.05, calculateTextLength("branches", 11, False, 600))
        self.assertAlmostEqual(
            765, calculateTextLength("coverage", 146 + 2 / 3, True, 600)
        )
        self.assertAlmostEqual(
            760.5, calculateTextLength("branches", 146 + 2 / 3, True, 600)
        )
        self.assertAlmostEqual(
            76.5, calculateTextLength("coverage", 14 + 2 / 3, True, 600)
        )
        self.assertAlmostEqual(
            76.05, calculateTextLength("branches", 14 + 2 / 3, True, 600)
        )

    def test_generateSVG(self):
        executedQueryResults = copy.deepcopy(executedQueryResultsOriginal)
        # UNCOMMENT: to generate SVG when user only owns forks, which should
        # have no repo stats, no languages chart, no most starred, no most forked.
        # self._changeToAllForks(executedQueryResults)
        class NoQueries(Statistician):
            def __init__(
                self,
                fail,
                autoLanguages,
                maxLanguages,
                languageRepoExclusions,
                featuredRepo,
            ):
                self._autoLanguages = autoLanguages
                self._maxLanguages = maxLanguages if maxLanguages >= 1 else 1
                self._languageRepoExclusions = languageRepoExclusions
                self._featuredRepo = featuredRepo
                self.parseStats(
                    executedQueryResults[0],
                    executedQueryResults[1],
                    executedQueryResults[2],
                    executedQueryResults[4],
                )
                self.parsePriorYearStats(executedQueryResults[3])

        stats = NoQueries(True, False, 100, set(), "FavoriteRepo")
        # stats._name = "Firstname ReallyLongMiddleName Lastname"
        # categories = ["general", "repositories", "languages", "contributions"]
        categories = categoryOrder[:]
        colors = copy.deepcopy(colorMapping["halloween"])
        # colors["title-icon"] = "pumpkin"
        svgGen = StatsImageGenerator(
            stats,
            colors,
            localeCode,
            6,
            18,
            categories,
            True,
            10,
            0,  # Doesn't matter since will autosize
            None,
            True,
            {},
        )
        image = svgGen.generateImage()
        if outputSampleSVG:
            writeImageToFile("testing.svg", image, False)

    def _colorValidation(self, theme):
        props = {"bg", "border", "icons", "text", "title"}
        validHexDigits = set("0123456789abcdefABCDEF")
        for p in props:
            color = theme[p]
            self.assertTrue(isValidColor(color))

    def _iconValidation(self, theme):
        self.assertTrue("title-icon" in theme)
        iconKey = theme["title-icon"]
        self.assertTrue(iconKey in iconTemplates)
        # deliberately used weird width, x, and y, to more easily verify they are inserted
        formattedIconString = iconTemplates[iconKey].format(
            83, 42, 53, "fake-color-to-confirm-inserted"
        )
        self.assertTrue(formattedIconString.find('width="83"') >= 0)
        self.assertTrue(formattedIconString.find('height="83"') >= 0)
        self.assertTrue(formattedIconString.find('x="42"') >= 0)
        self.assertTrue(formattedIconString.find('y="53"') >= 0)
        self.assertTrue(
            iconTemplates[iconKey].find("{3}") < 0
            or formattedIconString.find('fill="fake-color-to-confirm-inserted"') >= 0
        )

    def _validate(self, stats, skip=False):
        self.assertEqual("repo23", stats._user["mostStarred"][0])
        self.assertEqual("repo23", stats._user["mostForked"][0])
        self.assertEqual(2011, stats._user["joined"][0])
        self.assertEqual(9, stats._user["followers"][0])
        self.assertEqual(7, stats._user["following"][0])
        self.assertEqual(7, stats._user["sponsors"][0])
        self.assertEqual(5, stats._user["sponsoring"][0])
        self.assertEqual(29, stats._repo["public"][0])
        self.assertEqual(31, stats._repo["public"][1])
        self.assertEqual(36, stats._repo["starredBy"][0])
        self.assertEqual(36, stats._repo["starredBy"][1])
        self.assertEqual(28, stats._repo["forkedBy"][0])
        self.assertEqual(28, stats._repo["forkedBy"][1])
        self.assertEqual(3, stats._repo["watchedBy"][0])
        self.assertEqual(3, stats._repo["watchedBy"][1])
        self.assertEqual(2, stats._repo["archived"][0])
        self.assertEqual(2, stats._repo["archived"][1])
        self.assertEqual(1, stats._repo["templates"][0])
        self.assertEqual(1, stats._repo["templates"][1])
        self.assertEqual(3602, stats._contrib["commits"][0])
        self.assertEqual(4402, stats._contrib["commits"][1])
        self.assertEqual(79, stats._contrib["issues"][0])
        self.assertEqual(81, stats._contrib["issues"][1])
        self.assertEqual(289, stats._contrib["prs"][0])
        self.assertEqual(289, stats._contrib["prs"][1])
        self.assertEqual(315, stats._contrib["reviews"][0])
        self.assertEqual(315, stats._contrib["reviews"][1])
        self.assertEqual(3, stats._contrib["contribTo"][0])
        # self.assertEqual(8, stats._contrib["contribTo"][1])
        self.assertEqual(105, stats._contrib["private"][0])
        self.assertEqual(105, stats._contrib["private"][1])

        if skip:
            self._validateLanguagesSkip(stats)
        else:
            self._validateLanguages(stats)

    def _validateAllForks(self, stats):
        self.assertTrue("mostStarred" not in stats._user)
        self.assertTrue("mostForked" not in stats._user)
        self.assertEqual(2011, stats._user["joined"][0])
        self.assertEqual(9, stats._user["followers"][0])
        self.assertEqual(7, stats._user["following"][0])
        self.assertEqual(7, stats._user["sponsors"][0])
        self.assertEqual(5, stats._user["sponsoring"][0])
        self.assertEqual(0, stats._repo["public"][0])
        self.assertEqual(31, stats._repo["public"][1])
        self.assertEqual(0, stats._repo["starredBy"][0])
        self.assertEqual(36, stats._repo["starredBy"][1])
        self.assertEqual(0, stats._repo["forkedBy"][0])
        self.assertEqual(28, stats._repo["forkedBy"][1])
        self.assertEqual(0, stats._repo["watchedBy"][0])
        self.assertEqual(3, stats._repo["watchedBy"][1])
        self.assertEqual(0, stats._repo["archived"][0])
        self.assertEqual(2, stats._repo["archived"][1])
        self.assertEqual(0, stats._repo["templates"][0])
        self.assertEqual(1, stats._repo["templates"][1])
        self.assertEqual(3602, stats._contrib["commits"][0])
        self.assertEqual(4402, stats._contrib["commits"][1])
        self.assertEqual(79, stats._contrib["issues"][0])
        self.assertEqual(81, stats._contrib["issues"][1])
        self.assertEqual(289, stats._contrib["prs"][0])
        self.assertEqual(289, stats._contrib["prs"][1])
        self.assertEqual(315, stats._contrib["reviews"][0])
        self.assertEqual(315, stats._contrib["reviews"][1])
        self.assertEqual(3, stats._contrib["contribTo"][0])
        # self.assertEqual(8, stats._contrib["contribTo"][1])
        self.assertEqual(105, stats._contrib["private"][0])
        self.assertEqual(105, stats._contrib["private"][1])
        self.assertEqual(0, stats._languages["totalSize"])
        self.assertEqual(0, len(stats._languages["languages"]))

    def _validateLanguages(self, stats):
        total = 5222379
        self.assertEqual(total, stats._languages["totalSize"])
        self.assertEqual(11, len(stats._languages["languages"]))

        expectedLanguages = [
            "Java",
            "HTML",
            "Python",
            "TeX",
            "Dockerfile",
            "Makefile",
            "Shell",
            "GraphQL",
            "CSS",
            "JavaScript",
            "Batchfile",
        ]
        expectedColors = [
            "#b07219",
            "#e34c26",
            "#3572A5",
            "#3D6117",
            "#384d54",
            "#427819",
            "#89e051",
            "#e10098",
            "#563d7c",
            "#f1e05a",
            "#C1F12E",
        ]
        expectedSize = [
            3385976,
            1343301,
            274535,
            202824,
            5448,
            4442,
            1926,
            1902,
            1721,
            204,
            100,
        ]
        for i, L in enumerate(stats._languages["languages"]):
            self.assertEqual(expectedLanguages[i], L[0])
            self.assertEqual(expectedColors[i], L[1]["color"])
            self.assertEqual(expectedSize[i], L[1]["size"])
            self.assertAlmostEqual(
                expectedSize[i] / total, L[1]["percentage"], places=5
            )

    def _validateLanguagesSkip(self, stats):
        total = 5147159
        self.assertEqual(total, stats._languages["totalSize"])
        self.assertEqual(10, len(stats._languages["languages"]))

        expectedLanguages = [
            "Java",
            "HTML",
            "TeX",
            "Python",
            "Dockerfile",
            "Makefile",
            "Shell",
            "CSS",
            "JavaScript",
            "Batchfile",
        ]
        expectedColors = [
            "#b07219",
            "#e34c26",
            "#3D6117",
            "#3572A5",
            "#384d54",
            "#427819",
            "#89e051",
            "#563d7c",
            "#f1e05a",
            "#C1F12E",
        ]
        expectedSize = [
            3385976,
            1343301,
            202824,
            201574,
            5091,
            4442,
            1926,
            1721,
            204,
            100,
        ]
        for i, L in enumerate(stats._languages["languages"]):
            self.assertEqual(expectedLanguages[i], L[0])
            self.assertEqual(expectedColors[i], L[1]["color"])
            self.assertEqual(expectedSize[i], L[1]["size"])
            self.assertAlmostEqual(
                expectedSize[i] / total, L[1]["percentage"], places=5
            )

    def _changeToAllForks(self, queryResults):
        for repo in queryResults[1][0]["data"]["user"]["repositories"]["nodes"]:
            repo["isFork"] = True
        for repo in queryResults[4][0]["data"]["user"]["topRepositories"]["nodes"]:
            repo["isFork"] = True
        for repo in queryResults[2][0]["data"]["user"]["watching"]["nodes"]:
            repo["isFork"] = True
