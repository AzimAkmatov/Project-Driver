.PHONY: up down fmt test
up:
\tdocker compose -f docker-compose.dev.yml up --build
down:
\tdocker compose -f docker-compose.dev.yml down
fmt:
\tblack backend/app
test:
\tpytest -q
