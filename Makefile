image:
	docker-compose build

listener:
	python3 setup.py

install:
	make image
	make listener