#vim: set noexpandtab syntax=make
CWD	=$(shell pwd)
PYTHON =python3
PYTHON2=python2
PYTHON3_LIB_DIR =$(DESTDIR)/usr/lib/python3/dist-packages
PYTHON2_LIB_DIR=$(DESTDIR)/usr/lib/python2.7/dist-packages
PYTHON_MODULE_NAME=amqp
VCS_PUSH=git push origin master


bump:
	dch -m --release
	git add . -A
	git commit -m "bump version"
	git push origin master


clean:
	@find . | grep -E "(__pycache__|\.pyc$\)" | xargs rm -rf
	@rm -rf dist build
	@rm -rf *.egg-info
	@rm -rf ../*.orig.tar.gz
	@rm -rf *.egg-info


install-development-deps:
	pip3 install coverage nose pylint sphinx sphinxcontrib-napoleon==0.2.11\
		sphinx_rtd_theme==0.1.6

links:
	@make purge
	@ln -s $(CWD)/$(PYTHON_MODULE_NAME) $(PYTHON3_LIB_DIR)/$(PYTHON_MODULE_NAME)
	@ln -s $(CWD)/$(PYTHON_MODULE_NAME) $(PYTHON2_LIB_DIR)/$(PYTHON_MODULE_NAME)


purge:
	@rm -rf $(PYTHON3_LIB_DIR)/$(PYTHON_MODULE_NAME)
	@rm -rf $(PYTHON2_LIB_DIR)/$(PYTHON_MODULE_NAME)
