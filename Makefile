EXEC   := build
WHEEL  := corti

all: test

##-------------------------------------------------------------------
##                      Python dev convenience rules
##-------------------------------------------------------------------
bundle: clean ${EXEC}

dev:
	@pipenv install --dev
	@pipenv run pip install -e .
	@echo "installed development version; run \`pipenv shell\` to enter activated environment."

test:
	@pipenv run pytest --cov-report term-missing --cov=${WHEEL} tests/

lint:
	@pipenv run pylint --rcfile=.pylintrc ${WHEEL} -f parseable -r n
	@pipenv run mypy --ignore-missing-imports --follow-imports=skip ${WHEEL}
	@pipenv run pycodestyle ${WHEEL} --max-line-length=120
	@pipenv run pydocstyle ${WHEEL}

# Define all non-file tagets here
.PHONY: ${WHEEL} bundle clean mrproper lint test dev help

##-------------------------------------------------------------------
##                      Wheel building rules
##-------------------------------------------------------------------

${EXEC}: requirements.txt ${WHEEL}
	@echo "adding to pex"
	# build pex file
	@pipenv run pex --python-shebang='/usr/bin/env python3' -r $< -f wheels ${WHEEL} -c $@ -o $@
	@chmod 755 $@

requirements.txt: Pipfile
	@pipenv lock --requirements > $@

${WHEEL}:
	# generate a new one (deps should already be present)
	@pipenv run pip wheel -w wheels --no-deps .

##-------------------------------------------------------------------
##                      House keeping rules
##-------------------------------------------------------------------
clean:
	@rm -f ${EXEC}

mrproper: clean
	@rm -f wheels/* requirements.txt
