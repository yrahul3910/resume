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
    VERSION = "3.1.0"

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
        self.file.write(r"\begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}")
        self.file.write("\n")
        self.file.write(r"\textbf{\Large " + info["name"] + r"}\ifroleset,\fi \role &")
        self.file.write("\n")
        self.file.write(r"\href{mailto:" + info['contact']['email'] + "}{" + info["contact"]["email"] + r"} \\")

        hrefs = [r"\href{" + link["url"] + "}{" + link["display"] + "}" for link in info["links"]]
        self.file.write("\n")
        self.file.write(" :: ".join(hrefs) + f" & {info['contact']['phone']}")
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

            self.file.write(r"\resumeSubheading{" + school + "}{" + location + "}{" + degree + "}{" + dates + "}")
            self.file.write("\n")
        
        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_employment(self, after_date="1970-01-01"):
        if len(self.data["employment"]) == 0:
            return
        
        after_date = datetime.fromisoformat(after_date)
        
        self.file.write("\n")
        self.file.write("\\section{Employment}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        # Get a list of all the unique tags from the data
        tags = {}
        for entry in self.data["employment"]:
            pos_tags = [pos["tags"] for pos in entry["positions"]]
            # Flatten pos_tags
            pos_tags = [tag for tags in pos_tags for tag in tags]
            for tag in pos_tags:
                tags[tag] = False

        for entry in self.data["employment"]:
            company = entry["organization"]
            location = entry["location"]
            positions = entry["positions"]

            for tag in tags:
                tags[tag] = False

            for position in positions:
                # Check the tags in position. If that self.vars[tag] is True, then we 
                # include this position in the CV.
                cur_tags = position["tags"]
                set_tags = set([tag for tag in tags if tags[tag]])
                dates = self._get_str_from_dates(position["dates"])

                try:
                    pos_end_date = datetime.fromisoformat(position["dates"][1])

                    if pos_end_date < after_date:
                        continue
                except TypeError:
                    # Probably got null, which means we should not filter
                    pass

                if set(cur_tags).isdisjoint(set_tags):
                    self.file.write(rf"\resumeSubheading{{{company}}}{{{location}}}{{{position['position']}}}{{{dates}}}")
                else:
                    self.file.write(rf"\addExtraPosition{{{position['position']}}}{{{dates}}}")
                
                self.file.write(r"{ \resumeItemListStart")
                self.file.write("\n")

                for detail in position["details"]:
                    self.file.write(r"\item \small{" + detail + r" \vspace{-2pt}}")
                    self.file.write("\n")

                self.file.write(r"\resumeItemListEnd }")
                self.file.write("\n")

                for tag in cur_tags:
                    tags[tag] = True
        
        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_publications(self, latest_k=999):
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
            self.file.write(rf"\item \textbf{{{funding['amount']}}}, {funding['title']}, {date}")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_service(self):
        if len(self.data["service"]) == 0:
            return
        
        self.file.write("\n")
        self.file.write("\\section{Service to Profession}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for service in self.data["service"]:
            self.file.write(rf"\item \textbf{{{service['title']}}}, {service['details']}")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_honors(self):
        if len(self.data["honors"]) == 0:
            return
        
        self.file.write("\n")
        self.file.write("\\section{Honors and Awards}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for honor in self.data["honors"]:
            date = self._get_str_from_date(honor["date"])
            self.file.write(rf"\item {honor['title']}, {date}")
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
            self.file.write(rf"\item \textbf{{{date}}}, ``\textit{{{talk['title']}}}'' at {talk['location']}")
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
            key=lambda p: datetime.fromisoformat(p["dates"][1]) if p["dates"][1] is not None else datetime(3000, 1, 1),
            reverse=True
        )

        while k < latest_k and i < len(self.data["projects"]) - 1:
            project = self.data["projects"][i]
            i += 1
            if any([self.vars.get(tag, False) for tag in project["tags"]]):
                k += 1
                links = [rf"\href{{{link['url']}}}{{{link['display']}}}" for link in project["links"]]
                dates = self._get_str_from_dates(project["dates"])
                self.file.write(rf"\resumeSubheading{{{project['title']}}}{{{dates}}}{{{', '.join(project['skills'])}}}{{{' :: '.join(links)}}}")
                
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
            self.file.write(rf"\item \textbf{{{skill}}}: {', '.join(skills[skill])}")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")
