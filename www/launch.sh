PORT=${1:-5000}
flask --debug  --app app  run  --host 0.0.0.0 --port=$PORT
