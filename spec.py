import os
import json
from datetime import datetime
from packaging.version import parse as parse_version


class DataParser:
    """
    Parser for ML and SDE roles. It expects the following variables to have been set: master, sde, ml

    For master CV, set master to True
    For SDE CV, set sde to True
    For ML CV, set ml to True
    """

    VERSION = "3.2.0"

    def __init__(self, file, vars):
        self.file = file
        self.vars = vars

        if not os.path.exists("data.json"):
            raise RuntimeError("data.json not found")

        with open("data.json", "r") as f:
            self.data = json.load(f)

        if "version" not in self.data:
            raise RuntimeError("data.json missing version")

        if parse_version(self.data["version"]) > parse_version(self.VERSION):
            raise RuntimeError("data.json version is newer than spec.py version")

    def _get_str_from_date(self, date):
        try:
            return datetime.fromisoformat(date).strftime("%b %Y")
        except TypeError:
            return "Unknown"

    def _get_str_from_dates(self, dates):
        [start, end] = dates
        try:
            start = datetime.fromisoformat(start).strftime("%b %Y")
        except TypeError:
            start = "Present"

        try:
            end = datetime.fromisoformat(end).strftime("%b %Y")
        except TypeError:
            end = "Present"

        return f"{start} - {end}"

    def parse_begin(self):
        self.file.write(r"\begin{document}")
        self.file.write("\n")

    def parse_personalInfo(self):
        info = self.data["personalInfo"]

        if self.vars.get("ANONYMOUS_MODE", False):
            name = "Anonymous"
            phone = "Phone" if info["contact"]["phone"] else ""
            email = "Email" if info["contact"]["email"] else ""
        else:
            name = info["name"]
            phone = info["contact"]["phone"]
            email = info["contact"]["email"]

        self.file.write(r"\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}")
        self.file.write("\n")
        self.file.write(r"\textbf{\Large " + name + r"}\ifroleset,\fi \role &")
        self.file.write("\n")
        self.file.write(r"\href{mailto:" + email + "}{" + email + r"} \\")

        hrefs = []
        for link in info["links"]:
            url = link["url"]
            if self.vars.get("ANONYMOUS_MODE", False):
                url = url.split(".com")[0] + ".com"

            hrefs.append(r"\href{" + url + "}{" + link["display"] + "}")

        self.file.write("\n")
        self.file.write(" :: ".join(hrefs) + f" & {phone}")
        self.file.write(r" \\ \end{tabular*}")
        self.file.write("\n")

    def parse_education(self):
        if len(self.data["education"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Education}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for entry in self.data["education"]:
            school = entry["institution"]
            location = entry["location"]
            degree = entry["degree"]
            dates = self._get_str_from_dates(entry["dates"])
            details = entry.get("details", [])

            self.file.write(
                r"\resumeSubheading{"
                + school
                + "}{"
                + location
                + "}{"
                + degree
                + "}{"
                + dates
                + "}"
            )
            self.file.write("\n")
            self.file.write(r"{ \resumeItemListStart")
            self.file.write("\n")

            for detail in details:
                detail_title, *detail_desc = detail.split(":")
                self.file.write(
                    r"\item \small{"
                    + detail_title
                    + r":\textit{"
                    + ":".join(detail_desc)
                    + r"} \vspace{-4pt}}"
                )
                self.file.write("\n")

            self.file.write(r"\resumeItemListEnd }")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_employment(self, after_date="1970-01-01"):
        if len(self.data["employment"]) == 0:
            return

        after_date = datetime.fromisoformat(after_date)

        self.file.write("\n")
        self.file.write("\\section{Employment}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for entry in self.data["employment"]:
            company = entry["organization"]
            location = entry["location"]
            positions = entry["positions"]

            for i, position in enumerate(positions):
                # Check the tags in position. If that self.vars[tag] is True, then we
                # include this position in the CV.
                cur_tags = position["tags"]
                dates = self._get_str_from_dates(position["dates"])

                if cur_tags and not all(
                    [self.vars.get(tag, False) for tag in cur_tags]
                ):
                    continue

                try:
                    pos_end_date = datetime.fromisoformat(position["dates"][1])

                    if pos_end_date < after_date:
                        continue
                except TypeError:
                    # Probably got null, which means we should not filter
                    pass

                if i == 0:
                    self.file.write(
                        rf"\resumeSubheading{{{company}}}{{{location}}}{{{position['position']}}}{{{dates}}}"
                    )
                else:
                    self.file.write(
                        rf"\addExtraPosition{{{position['position']}}}{{{dates}}}"
                    )

                self.file.write(r"{ \resumeItemListStart")
                self.file.write("\n")

                for detail in position["details"]:
                    self.file.write(r"\item \small{" + detail + r" \vspace{-2pt}}")
                    self.file.write("\n")

                self.file.write(r"\resumeItemListEnd }")
                self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_publications(self, latest_k=999):
        if self.vars.get("ANONYMOUS_MODE", False):
            return

        if len(self.data["publications"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Recent Publications}\n")
        self.file.write("See full list on Google Scholar.")
        self.file.write("\\resumeNumberedSubHeadingListStart\n")

        i = 0
        while i < len(self.data["publications"]) and i < latest_k:
            publication = self.data["publications"][i]
            self.file.write(rf"\item {publication}")
            self.file.write("\n")
            i += 1

        self.file.write("\\resumeNumberedSubHeadingListEnd\n\n")

    def parse_funding(self):
        if len(self.data["funding"]) == 0:
            return

        self.file.write("\\section{Funding}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for funding in self.data["funding"]:
            date = self._get_str_from_date(funding["date"])
            self.file.write(
                rf"\item \textbf{{{funding['amount']}}}, {funding['title']}, {date}"
            )
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_service(self):
        if len(self.data["service"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Service to Profession}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for service in self.data["service"]:
            if "hidden" in service and service["hidden"]:
                continue

            self.file.write(
                rf"\item \textbf{{{service['title']}}}, {service['details']}"
            )
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_honors(self):
        if len(self.data["honors"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Honors}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for honor in self.data["honors"]:
            if honor.get("hidden", False):
                continue

            if isinstance(honor["date"], str):
                date = self._get_str_from_date(honor["date"])
            elif isinstance(honor["date"], list):
                date = self._get_str_from_dates(honor["date"])
            else:
                raise ValueError(f"Honor {honor['title']} needs a valid date.")

            if "details" in honor:
                self.file.write(
                    rf"\resumeSubheading{{{honor['title']}}}{{{date}}}{{}}{{}}"
                )
                if len(honor["details"]) == 1:
                    self.file.write(rf"\projectDescription{{{honor['details'][0]}}}")
                else:
                    self.file.write(r"{ \resumeItemListStart")
                    self.file.write("\n")

                    for detail in honor["details"]:
                        self.file.write(r"\item \small{" + detail + r" \vspace{-2pt}}")
                        self.file.write("\n")

                    self.file.write(r"\resumeItemListEnd }")
                    self.file.write("\n")
            else:
                self.file.write(rf"\item \textbf{{{date}}} - {honor['title']}")
                self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_talks(self):
        if len(self.data["talks"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Invited Talks}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for talk in self.data["talks"]:
            date = self._get_str_from_date(talk["date"])
            self.file.write(
                rf"\item \textbf{{{date}}}, ``\textit{{{talk['title']}}}'' at {talk['location']}"
            )
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_projects(self, latest_k=999):
        if len(self.data["projects"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Relevant Projects}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        k = 0
        i = 0

        # Re-arrange self.data["projects"] in descending order of completion date.
        self.data["projects"].sort(
            key=lambda p: (
                datetime.fromisoformat(p["dates"][1])
                if p["dates"][1] is not None
                else datetime(3000, 1, 1)
            ),
            reverse=True,
        )

        while k < latest_k and i < len(self.data["projects"]) - 1:
            project = self.data["projects"][i]
            i += 1

            if "hidden" in project and project["hidden"]:
                continue

            if not project["tags"] or any(
                [self.vars.get(tag, False) for tag in project["tags"]]
            ):
                k += 1
                links = []
                for link in project["links"]:
                    url = link["url"]
                    if self.vars.get("ANONYMOUS_MODE", False):
                        url = url.split(".com")[0] + ".com"

                    links.append(r"\href{" + url + "}{" + link["display"] + "}")

                dates = self._get_str_from_dates(project["dates"])
                self.file.write(
                    rf"\resumeSubheading{{{project['title']}}}{{{dates}}}{{{', '.join(project['skills'])}}}{{{' :: '.join(links)}}}"
                )

                if len(project["details"]) == 1:
                    self.file.write(rf"\projectDescription{{{project['details'][0]}}}")
                else:
                    self.file.write(r"{ \resumeItemListStart")
                    self.file.write("\n")

                    for detail in project["details"]:
                        self.file.write(r"\item \small{" + detail + r" \vspace{-2pt}}")
                        self.file.write("\n")

                    self.file.write(r"\resumeItemListEnd }")
                    self.file.write("\n")

                self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")

    def parse_skills(self):
        if len(self.data["skills"]) == 0:
            return

        self.file.write("\n")
        self.file.write("\\section{Skills}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        # Get map from skill type to list of skills
        skills = {}
        for skill in self.data["skills"]:
            if skill["type"] not in skills:
                skills[skill["type"]] = []
            skills[skill["type"]].append(skill["name"])

        for skill in skills:
            self.file.write(rf"\item \textbf{{{skill}}}: {', '.join(skills[skill])} ")
            self.file.write(r"\vspace{-4pt}")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")
