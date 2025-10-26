.PHONY: bootstrap dev lint fmt typecheck test e2e coverage build package release update-deps security-scan sbom gen-docs migrate clean check license-scan

bootstrap:
	./scripts/bootstrap

dev:
	./scripts/dev

lint:
	./scripts/lint

fmt:
	./scripts/fmt

typecheck:
	./scripts/typecheck

test:
	./scripts/test

e2e:
	./scripts/e2e

coverage:
	./scripts/coverage

build:
	./scripts/build

package:
	./scripts/package

release:
	./scripts/release

update-deps:
	./scripts/update-deps

security-scan:
	./scripts/security-scan

license-scan:
	./scripts/license-scan

sbom:
	./scripts/sbom

gen-docs:
	./scripts/gen-docs

migrate:
	./scripts/migrate

clean:
	./scripts/clean

check:
	./scripts/check
