# Installing dependencies
```shell
$ uv venv
$ source .venv/bin/activate
$ uv pip install -r requirements.txt
```

# Setting up `pre-commit` hooks
```shell
$ pre-commit install
# Manually run `pre-commit`
$ pre-commit run --all-files
```

# Running the required services
```shell
$ docker-compose up
```

# Running the application
```shell
$ flask run
```

# Installing the UI dependencies and running it
```shell
$ bun install
$ burn run dev
```
