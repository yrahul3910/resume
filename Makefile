.PHONY: all

all:
	progres -o pdf -d

clean:
	rm *.aux *.log *.out *.synctex.gz *.pdf {sde,ml,master,academic}.py {sde,ml,master,academic}.tex 2>/dev/null || true
