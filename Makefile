.PHONY: build serve serve_detach kill kill_mac remove_image local_run

app_name = aws-meetup:latest
docker_file = Dockerfile

build:
	docker build -t $(app_name) -f $(docker_file) .

serve:
	docker run -p 8080:8080 $(app_name)

serve_detach:
	docker run --detach -p 8080:8080 $(app_name)


kill:
	@echo 'Killing container...'
	docker ps | grep $(app_name) | awk '{print $$1}' | xargs -r docker stop

kill_mac:
	@echo 'Killing container...'
	docker ps | grep $(app_name) | awk '{print $$1}' | xargs docker stop

remove_image:
	docker ps -a | grep $(app_name) | awk '{print $$1}' | xargs docker rm

local_run:
	PYTHONPATH=clientside streamlit run clientside/main.py