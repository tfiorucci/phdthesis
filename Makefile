DOCNAME=dissertation

all:
	report

.PHONY: clean

thesis:
	pdflatex $(DOCNAME).tex
	biber $(DOCNAME)
	pdflatex $(DOCNAME).tex
	pdflatex $(DOCNAME).tex

view: thesis
	evince $(DOCNAME).pdf

clean:
	rm *.blg *.bbl *.aux *.log
