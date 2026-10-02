.PHONY: all

all:
	rm -f pdf/*
	progres -o pdf -d
	cp pdf/sde.pdf "pdf/RahulYedida_SoftwareEngineer.pdf"
	mv pdf/sde.pdf "pdf/RahulYedida_AIEngineer.pdf"
	mv pdf/ml.pdf "pdf/RahulYedida_MLEngineer.pdf"
	mv pdf/academic.pdf "pdf/RahulYedida_ResearchScientist.pdf"

clean:
	rm *.aux *.log *.out *.synctex.gz *.pdf {sde,ml,master,academic}.py {sde,ml,master,academic}.tex 2>/dev/null || true
