import os
import json

class DataParser:
    """
    Parser for ML and SDE roles. It expects the following variables to have been set: master, sde, ml

    For master CV, set master to True
    For SDE CV, set sde to True
    For ML CV, set ml to True
    """
    def __init__(self, file, vars):
        self.file = file
        self.vars = vars

        if not os.path.exists("data.json"):
            raise RuntimeError("data.json not found")

        with open("data.json", "r") as f:
            self.data = json.load(f)
    
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

        hrefs = ["\href{" + link["url"] + "}{" + link["display"] + "}" for link in info["links"]]
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
            dates = entry["dates"]

            self.file.write(r"\resumeSubheading{" + school + "}{" + location + "}{" + degree + "}{" + dates + "}")
            self.file.write("\n")
        
        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_employment(self):
        if len(self.data["employment"]) == 0:
            return
        
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
                if set(cur_tags).isdisjoint(set_tags):
                    self.file.write(rf"\resumeSubheading{{{company}}}{{{location}}}{{{position['position']}}}{{{position['dates']}}}")
                else:
                    self.file.write(rf"\addExtraPosition{{{position['position']}}}{{{position['dates']}}}")
                
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
    
    def parse_publications(self):
        if len(self.data["publications"]) == 0:
            return
        
        self.file.write("\n")
        self.file.write("\\section{Publications}\n")
        self.file.write("\\resumeNumberedSubHeadingListStart\n")

        for publication in self.data["publications"]:
            self.file.write(rf"\item {publication}")
            self.file.write("\n")

        self.file.write("\\resumeNumberedSubHeadingListEnd\n\n")
    
    def parse_funding(self):
        if len(self.data["funding"]) == 0:
            return
        
        self.file.write("\\section{Funding}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for funding in self.data["funding"]:
            self.file.write(rf"\item \textbf{{{funding['amount']}}}, {funding['title']}, {funding['date']}")
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
            self.file.write(rf"\item {honor['title']}, {honor['date']}")
            self.file.write("\n")

        self.file.write("\\resumeSubHeadingListEnd\n\n")
    
    def parse_projects(self):
        if len(self.data["projects"]) == 0:
            return
        
        self.file.write("\n")
        self.file.write("\\section{Relevant Projects}\n")
        self.file.write("\\resumeSubHeadingListStart\n")

        for project in self.data["projects"]:
            if any([self.vars.get(tag, False) for tag in project["tags"]]):
                links = [rf"\href{{{link['url']}}}{{{link['display']}}}" for link in project["links"]]
                self.file.write(rf"\resumeSubheading{{{project['title']}}}{{{project['dates']}}}{{{', '.join(project['skills'])}}}{{{' :: '.join(links)}}}")
                
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
